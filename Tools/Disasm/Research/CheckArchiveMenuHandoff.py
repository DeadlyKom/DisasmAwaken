"""Цепочка архивных RUN, START и ENGINE с восстановлением первых букв в модели каталога."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory, load_rom_file
from CheckBasicIntroDiskRead import prepare_memory
from CheckControlsLegacySectorRead import run_with_rom
from CheckFighterArchiveConsumer import service_requests, word
from CheckStartArchiveMenu import check_menu
from CheckStationFlightCycle import DISK, payload, put, run_to
from TraceFlight import H, IFF, L, PC, ROOT, SP, T, Simulator
from skoolkit.simutils import HALT, IM

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ExtractTrd import store


START_OFFSET = 0x8C200
ENGINE_OFFSET = 0x8B100
ROUTE_END = 0x942C7
TRANSFER_ENTRY = 0x40A9
STREAM_TAIL_START, STREAM_TAIL_END = 0x5C26, 0x5C36
ARCHIVE_ROWS = (
    (44, b'MK-II.d2B', 0x001C, 0x001C, 0x87300),
    (45, b'RUN     C', 0x6000, 0x3CDD, 0x87400),
    (46, b'ENGINE  C', 0x8000, 0x105B, ENGINE_OFFSET),
    (47, b'START   C', 0x6000, ROUTE_END - START_OFFSET, START_OFFSET),
)


class ArchiveBootPorts(BasicReadPorts):
    def read_port(self, registers, port, offset=0):
        if registers[PC] == 0x3D4F and port & 255 == 0xF6:
            return 255
        return super().read_port(registers, port, offset)


class HandoffMemory(ExtendedMemory):
    START_FIXED_SPANS = ((0x63E1, 0x6400), (0x6725, 0x675B), (0x677C, 0x67A4), (0x6C87, 0x6C8A))
    START_FIXED_BYTES = frozenset(address for start, end in START_FIXED_SPANS for address in range(start, end))
    ENGINE_UNCERTAIN = ((0x40A9, 0x40B1), (0x4617, 0x4627), (0x4D4D, 0x4D4F), (0x5C26, 0x5C27))
    ENGINE_UNCERTAIN_BYTES = frozenset(address for start, end in ENGINE_UNCERTAIN for address in range(start, end))

    def __init__(self, mode):
        self.mode = mode
        self.raw_7ffd = 0x10
        self.extended_page_bit = 0
        self.atm_window_pages = [0, 0]
        super().__init__()
        self.selection_reads = Counter()
        self.engine_key_reads = Counter()
        self.uncertain_accesses = Counter()
        self.gap_first_writes = {}
        self.gap_reads_before_write = Counter()
        self.overwritten_gap_read_sites = Counter()
        self.basic_copy_writes = []
        self.start_fixed_accesses = Counter()
        self.stream_tail_writes = Counter()
        self.watch_basic_copy = False
        self.watch_start = False
        self.watch_engine = False
        self.watch_stream_tail = False

    def out7ffd(self, value):
        self.raw_7ffd = value
        # Общий наблюдатель хранит старший бит страницы в позиции Pentagon.
        if self.mode == 1:
            value = (value & ~0x40) | (self.extended_page_bit << 6)
        elif self.mode == 2:
            upper_page_bit = self.atm_window_pages[(value >> 4) & 1]
            value = (value & ~0x40) | (upper_page_bit << 6)
        super().out7ffd(value)

    def out1ffd(self, value):
        assert self.mode == 1 and value in (0, 0x10)
        self.extended_page_bit = value >> 4
        self.out7ffd(self.raw_7ffd)

    def outfff7(self, value):
        # Исходное верхнее окно ATM-2 настроено на ОЗУ и объединение с #7FFD.
        assert self.mode == 2 and value & 0xC0 == 0xC0
        self.atm_window_pages[(self.raw_7ffd >> 4) & 1] = (~value >> 3) & 1
        rom = self.memory[0]
        self.out7ffd(self.raw_7ffd)
        # Перенастройка верхнего окна не отключает TR-DOS перед RET по #2A55.
        self.memory[0] = rom

    def current_gap_byte(self, address):
        if not isinstance(address, int) or not 0xDB4E <= address < self.read_watch_end:
            return None
        page = (self.o7ffd & 7) | ((self.o7ffd & 0x40) >> 3)
        bounds = self.unclassified_ranges.get(page)
        if bounds and bounds[0] <= address < bounds[1]:
            return page, address
        return None

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.watch_start and isinstance(address, int) and address in self.START_FIXED_BYTES:
            self.start_fixed_accesses['read', self.cpu.registers[PC], address] += 1
        if self.watch_engine and isinstance(address, int):
            pc = self.cpu.registers[PC]
            if address == 0x5F5E or 0x664B <= address < 0x664F:
                self.selection_reads[pc, address, value] += 1
            if 0x47FA <= address < 0x4842 or 0x5049 <= address < 0x505B:
                self.engine_key_reads[pc, address, value] += 1
            if address in self.ENGINE_UNCERTAIN_BYTES:
                self.uncertain_accesses['read', pc, address] += 1
            key = self.current_gap_byte(address)
            if key is not None:
                if key in self.gap_first_writes:
                    self.overwritten_gap_read_sites[key[0], pc] += 1
                else:
                    self.gap_reads_before_write[key] += 1
        return value

    def __setitem__(self, address, value):
        super().__setitem__(address, value)
        if self.watch_stream_tail and isinstance(address, int) and STREAM_TAIL_START <= address < STREAM_TAIL_END:
            self.stream_tail_writes[self.cpu.registers[PC], address, value] += 1
        if self.watch_basic_copy and isinstance(address, int) and self.cpu.registers[PC] == 0x2FF0:
            self.basic_copy_writes.append((address, value))
        if self.watch_start and isinstance(address, int) and address in self.START_FIXED_BYTES:
            self.start_fixed_accesses['write', self.cpu.registers[PC], address] += 1
        if self.watch_engine:
            if isinstance(address, int) and address in self.ENGINE_UNCERTAIN_BYTES:
                self.uncertain_accesses['write', self.cpu.registers[PC], address] += 1
            key = self.current_gap_byte(address)
            if key is not None:
                self.gap_first_writes.setdefault(key, (self.cpu.registers[PC], value))

    def start_fixed_summary(self):
        rows = []
        for start, end in self.START_FIXED_SPANS:
            reads, writes = Counter(), Counter()
            read_sites, write_sites = Counter(), Counter()
            for (operation, pc, address), count in self.start_fixed_accesses.items():
                if start <= address < end:
                    addresses, sites = (reads, read_sites) if operation == 'read' else (writes, write_sites)
                    addresses[address] += count
                    sites[pc] += count
            rows.append(dict(start=start, end_exclusive=end, read_addresses=sorted(reads),
                             written_addresses=sorted(writes), read_sites=read_sites, write_sites=write_sites))
        irq_stack = rows[2]
        assert list(range(0x6792, 0x67A4)) == irq_stack['written_addresses'][-18:]
        assert 0x67AC in irq_stack['write_sites']  # PUSH IX в начале IRQ
        assert all(not row['read_addresses'] and not row['written_addresses'] for row in (rows[0], rows[1], rows[3]))
        return rows

    def gap_lifetime(self):
        result = []
        for page, (start, end) in sorted(self.unclassified_ranges.items()):
            raw = payload(33 + page - 8)[start - 0xC000:end - 0xC000]
            assert raw == bytes(end - start)
            first_writes = {address: self.gap_first_writes[page, address]
                            for address in range(start, end) if (page, address) in self.gap_first_writes}
            source_slot = 40 + page - 8 if page < 12 else 30 if page == 13 else None
            first_write_pc = 0x3FEC if page < 12 else 0x495E
            if source_slot is not None:
                source = payload(source_slot)[start - 0xC000:end - 0xC000]
                assert first_writes == {address: (first_write_pc, value)
                                        for address, value in enumerate(source, start)}
            else:
                assert not first_writes and bytes(self.banks[page][start - 0xC000:end - 0xC000]) == raw
            reads_before = sum(self.gap_reads_before_write[page, addr] for addr in range(start, end))
            read_sites = {pc: count for (read_page, pc), count in self.overwritten_gap_read_sites.items()
                          if read_page == page}
            total = sum(self.unclassified_reads[page, addr] for addr in range(start, end))
            assert reads_before + sum(read_sites.values()) == total, (page, reads_before, read_sites, total)
            result.append(dict(page=page, start=start, end_exclusive=end,
                               overwritten_bytes=len(first_writes),
                               first_write_pc=first_write_pc if first_writes else None,
                               first_write_source_slot=source_slot,
                               reads_before_overwrite=reads_before,
                               reads_after_overwrite=sum(read_sites.values()),
                               read_sites_after_overwrite=read_sites))
        return result

    def check_engine_file_keys(self):
        keys = b''.join(f'BD{i}     C'.encode('ascii') for i in range(4))
        assert bytes(self[0x47FA:0x481E]) == bytes(self[0x481E:0x4842]) == keys
        bar_keys = b'BAR     C' * 2
        assert bytes(self[0x5049:0x505B]) == bar_keys
        regions = ((0x46AB, 0x47FA, keys), (0x467A, 0x5049, bar_keys[:9]), (0x468F, 0x5052, bar_keys[9:]))
        expected = Counter((pc, address, value) for pc, start, data in regions
                           for address, value in enumerate(data, start))
        assert self.engine_key_reads == expected, self.engine_key_reads - expected
        return dict(used_bd_range=[0x47FA, 0x481E], identical_bd_range=[0x481E, 0x4842],
                    identical_bd_reads=0,
                    used_regions=[dict(pc=pc, start=start, end_exclusive=start + len(data))
                                  for pc, start, data in regions])

    def uncertain_summary(self):
        return [dict(start=start, end_exclusive=end,
                     accesses=[dict(kind=kind, pc=pc, address=address, count=count)
                               for (kind, pc, address), count in sorted(self.uncertain_accesses.items())
                               if start <= address < end])
                for start, end in self.ENGINE_UNCERTAIN]


def check_catalogue_residue():
    assert 0x9406F + 12 * 50 == ROUTE_END
    rows = []
    for offset, key in ((0x942C0, None), (0x942D0, b'OFILD   C'),
                        (0x942E0, b'MKCOD   C'), (0x942F0, b'selnumb s')):
        header = DISK[offset:offset + 16]
        if key:
            assert header[:9] == key
        else:
            assert header[7:9] == b' C'
        length = int.from_bytes(header[11:13], 'little')
        count, sector, track = header[13:16]
        assert (length + 255) // 256 == count and sector < 16
        rows.append(dict(disk_offset=offset, name=key.decode('ascii') if key else None,
                         origin=int.from_bytes(header[9:11], 'little'), logical_bytes=length,
                         sector_count=count, old_start_lba=16 * track + sector))
    assert all(a['old_start_lba'] + a['sector_count'] == b['old_start_lba'] for a, b in zip(rows, rows[1:]))
    assert all(row['old_start_lba'] * 256 < ENGINE_OFFSET for row in rows)
    return rows


def catalogue_fixture():
    disk = bytearray(DISK)
    entries = []
    for slot, key, parameter, length, offset in ARCHIVE_ROWS:
        position = 16 * slot
        header = disk[position:position + 16]
        assert header[:9] == bytes(1) + key[1:]
        assert int.from_bytes(header[9:11], 'little') == parameter
        assert int.from_bytes(header[11:13], 'little') == length
        assert header[13] == (length + 255) // 256
        assert (16 * header[15] + header[14]) * 256 == offset
        disk[position] = key[0]
        entries.append(dict(slot=slot, model_key=key.decode('ascii'), raw_header_hex=header.hex(),
                            catalogue_parameter=parameter, original_header_offset=position,
                            logical_length=length, original_disk_offset=offset, physical_sectors=header[13]))
    assert all(a['original_disk_offset'] + a['physical_sectors'] * 256 == b['original_disk_offset']
               for a, b in zip(entries, entries[1:]))
    assert disk[0x8E4] == 44
    disk[0x8E4] = 48
    assert disk[0x1000:] == DISK[0x1000:]
    assert {index for index, (a, b) in enumerate(zip(DISK, disk)) if a != b} == {16 * i for i in range(44, 48)} | {0x8E4}
    return bytes(disk), entries


def extract_archive_rows(entries):
    for row in entries:
        slot, offset, length = row['slot'], row['original_disk_offset'], row['logical_length']
        name = row['model_key'][:8].rstrip() if slot != 44 else '_K-II.d2'
        stem = f"Tools/Disasm/Extracted/Archived/{slot:02d}_{name}.{row['model_key'][-1]}"
        sectors = DISK[offset:offset + row['physical_sectors'] * 256]
        position = row['original_header_offset']
        row['extracted'] = dict(header=store(stem + '.header.bin', DISK[position:position + 16]),
                                logical=store(stem + '.bin', sectors[:length]),
                                sectors=store(stem + '.sectors.bin', sectors),
                                tail=store(stem + '.tail.bin', sectors[length:]))


class HandoffPorts(ArchivePorts):
    def __init__(self, memory):
        super().__init__(memory)
        self.paging_writes = Counter()

    def write_port(self, registers, port, value, offset):
        if port in (0x1FFD, 0x7FFD, 0xFFF7):
            self.paging_writes[registers[PC], port, value] += 1
        if port == 0x1FFD:
            self.memory.out1ffd(value)
        elif port == 0xFFF7:
            assert registers[PC] == 0x2A53
            self.memory.outfff7(value)
        else:
            super().write_port(registers, port, value, offset)


def check_transfer_word_references():
    def offsets(word):
        value = word.to_bytes(2, 'little')
        return [offset for offset in range(len(DISK) - 1) if DISK[offset:offset + 2] == value]

    incoming = offsets(TRANSFER_ENTRY)
    outgoing = offsets(STREAM_TAIL_START)
    direct_branch_opcodes = {0xC3, 0xCD, *range(0xC2, 0x100, 8), *range(0xC4, 0x100, 8)}
    assert len(incoming) == 14 and all(offset and DISK[offset - 1] not in direct_branch_opcodes for offset in incoming)
    assert outgoing == [ENGINE_OFFSET + 0xAF] and DISK[outgoing[0] - 1] == 0xC3
    return dict(image_bytes=len(DISK), entry_word_offsets=incoming, destination_word_offsets=outgoing,
                direct_absolute_branch_to_entry_candidates=0)


def check_forced_transfer(cpu, advance):
    memory, registers = cpu.memory, cpu.registers
    before = bytes(memory[STREAM_TAIL_START:STREAM_TAIL_END])
    assert before == bytes(STREAM_TAIL_END - STREAM_TAIL_START) and not memory.stream_tail_writes
    sp, iff = registers[SP], registers[IFF]
    registers[PC], registers[HALT] = TRANSFER_ENTRY, 0
    advance(cpu, STREAM_TAIL_START)
    assert memory.o7ffd == 0x18 and memory[0x5012] == 0
    assert (registers[SP], registers[IFF]) == (sp, iff)
    for address in range(STREAM_TAIL_START, STREAM_TAIL_END):
        assert registers[PC] == address and memory[address] == 0
        cpu.run()
    assert registers[PC] == STREAM_TAIL_END and (registers[SP], registers[IFF]) == (sp, iff)
    assert bytes(memory[STREAM_TAIL_START:STREAM_TAIL_END]) == before and not memory.stream_tail_writes
    return dict(entry=TRANSFER_ENTRY, destination=STREAM_TAIL_START, initial_bytes=before.hex(),
                normal_path_write_count=0, forced_nops=len(before), stopped_at=STREAM_TAIL_END,
                final_page=0, sp=sp, iff=iff)


def check_handoff(rom, disk, entries, *, mode=0, change_selection=False):
    basic, dos, system = rom
    basic_row, run_row, engine_row, start_row = entries
    bootstrap_report = {}

    def bootstrap(memory):
        start = basic_row['original_disk_offset']
        assert DISK[start:start + 28] == bytes.fromhex(
            '00 01 18 00 F9 C0 31 35 36 31 39 0E 00 00 03 3D 00 3A EA 3A F7 22 52 55 4E 22 AF 0D')
        origin, stack = 0x5D3B, 0xFEFE
        memory.roms = (basic, basic)
        memory.out7ffd(0x10)
        put(memory, 0x5C00, prepare_memory(basic)[0x5C00:0x5D3E])
        # CHANS после инициализации TR-DOS, иначе #3D03 очищает BASIC заново.
        put(memory, 0x5C4F, b'\x25\x5D')
        # Редактор ищет опубликованное имя, восстановленное только в модели каталога.
        line = b'\xF7"' + basic_row['model_key'][:8].encode('ascii') + b'"\r\x80'
        put(memory, origin + 1, line)
        for address in (0x5C61, 0x5C63, 0x5C65):
            put(memory, address, (origin + 1 + len(line)).to_bytes(2, 'little'))
        memory[0x5CB6], memory[0x5D0C], memory[0x5CF8], memory[0x5C3B] = 0xF4, 0xFF, 0, 0x80
        put(memory, 0x5D13, b'\x54\xFF')
        put(memory, 0x5D1A, b'\xCB\x02')
        put(memory, 0x5D1C, stack.to_bytes(2, 'little'))
        cpu = Simulator(memory, {'PC': 0x02FC, 'SP': stack, 'IY': 0x5C3A}, state={'im': 1},
                        config={'fast_ldir': False, 'fast_djnz': True})
        memory.cpu = cpu
        ports = ArchiveBootPorts(memory)
        ports.disk = disk
        cpu.set_tracer(ports)

        def set_rom(image):
            memory.memory[0] = image

        memory.watch_stream_tail = True
        memory.watch_basic_copy = True
        run_with_rom(cpu, basic, dos, set_rom, 0x012A, initial_dos=True)
        memory.watch_basic_copy = False
        assert ports.attempts[-1] == (0x87, 4)
        raw_sector = DISK[start:start + 256]
        staged = int.from_bytes(memory[0x5C53:0x5C55], 'little')
        assert bytes(memory[0x5D25:0x5E25]) == raw_sector
        assert bytes(memory[staged:staged + 33]) == raw_sector[:33]
        assert memory.basic_copy_writes == list(enumerate(raw_sector[:33], staged))
        assert raw_sector[28:33] == b'\x80\xAA\x00\x00k'
        run_with_rom(cpu, basic, dos, set_rom, 0x3D03, initial_dos=True)
        try:
            run_with_rom(cpu, basic, dos, set_rom, 0x6000, initial_dos=True, step_limit=1_000_000)
        except AssertionError as error:
            raise AssertionError((f'{cpu.registers[PC]:04X}', ports.attempts, memory[0x5D0F],
                                  bytes(memory[0x5D3B:0x5D57]).hex(), memory.memory[0] == dos)) from error
        run_start = run_row['original_disk_offset']
        raw = DISK[run_start:run_start + run_row['logical_length']]
        assert bytes(memory[0x6000:0x6000 + len(raw)]) == raw
        assert memory[0x5D0F] == 0
        data_reads = [item for item in ports.read_destinations if item[0][0]]
        expected_sectors = [divmod(index, 16)
                            for index in range(start // 256, run_start // 256 + run_row['physical_sectors'])]
        assert [sector for sector, _ in data_reads] == [(track, sector + 1) for track, sector in expected_sectors]
        assert data_reads[0] == ((0x87, 4), 0x5D25)
        assert data_reads[-1] == ((0x8B, 1), 0x5D25)
        bootstrap_report.update(basic_first_character_fixture=basic_row['model_key'][0],
                                basic_disk_offset=start, basic_length=28,
                                staged_basic_origin=staged, staged_basic_prefix_bytes=33,
                                autostart_marker_hex=raw_sector[28:32].hex(), next_staged_byte=raw_sector[32],
                                executed_usr=0x3D03, run_entry=0x6000, run_data_sectors=61,
                                data_reads=len(data_reads), last_sector=data_reads[-1])
        return cpu

    def enter(cpu):
        memory, registers = cpu.memory, cpu.registers
        ports = BasicReadPorts(memory)
        ports.disk = disk
        archive_ports = HandoffPorts(memory)

        def set_rom(image):
            memory.memory[0] = image

        def advance(cpu, target):
            if mode == 2:
                run_with_rom(cpu, basic, dos, set_rom, target)
            else:
                run_to(cpu, target)

        def load_restored(row, address):
            key = row['model_key'].encode('ascii')
            offset, length = row['original_disk_offset'], row['logical_length']
            assert registers[PC] == 0x3D13 and bytes(memory[0x5CDD:0x5CE6]) == key
            assert registers[H] * 256 + registers[L] == address
            end = address + length
            before = bytes(memory[end:end + 16])
            start = len(ports.read_destinations)
            cpu.set_tracer(ports)
            set_rom(basic)
            run_with_rom(cpu, basic, dos, set_rom, address, step_limit=1_000_000)
            assert bytes(memory[address:end]) == DISK[offset:offset + length]
            assert bytes(memory[end:end + 16]) == before
            expected_sp = 0x6000 if address == 0x6000 else 0x6790
            assert memory[0x5D0F] == 0 and registers[SP] == expected_sp, (key, memory[0x5D0F], registers[SP])
            full, tail = divmod(length, 256)
            destinations = [address + 256 * i for i in range(full)] + [0x5D25]
            expected = []
            for index, destination in enumerate(destinations, offset // 256):
                track, sector = divmod(index, 16)
                expected.append(((track, sector + 1), destination))
            actual = [item for item in ports.read_destinations[start:] if item[0][0]]
            assert actual == expected
            return dict(key=key.decode('ascii'), origin=address, original_disk_offset=offset,
                        logical_length=length, logical_tail_bytes=tail, physical_reads=len(actual),
                        final_read=actual[-1], sp_on_entry=registers[SP])

        start = load_restored(start_row, 0x6000)
        assert memory[0x5F5E] == mode
        memory.watch_start = True
        cpu.set_tracer(archive_ports)
        for slot, page in zip(range(31, 39), (0x15, 0x1F, *range(0x58, 0x5E))):
            advance(cpu, 0x3D13)
            assert memory.o7ffd == page and bytes(memory[0x5CDD:0x5CE6]) == DISK[slot * 16:slot * 16 + 9]
            cpu.set_tracer(ports)
            load_rom_file(cpu, ports, (basic, dos), word(memory, registers[SP]), slot, payload(slot))
            cpu.set_tracer(archive_ports)
        advance(cpu, 0x6053)
        assert registers[IFF] and registers[SP] == 0x6000
        cpu.run()
        def bank_frame():
            registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
            assert cpu.accept_interrupt(registers, memory, 0x6060)
            advance(cpu, 0x6054)
            cpu.run()
            advance(cpu, 0x6054)

        for _ in range(32):
            bank_frame()
        initial_selection = bytes(memory[0x664B:0x664F])
        if change_selection:
            archive_ports.menu_key = (0xFDFE, 4)
            for _ in range(8):
                bank_frame()
                if bytes(memory[0x664B:0x664F]) != initial_selection:
                    break
            assert bytes(memory[0x664B:0x664F]) == bytes((initial_selection[0] + 1,)) + initial_selection[1:]
            archive_ports.menu_key = None
            for _ in range(4):
                bank_frame()
        selection_at_enter = bytes(memory[0x664B:0x664F])
        archive_ports.enter_pressed = True
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        assert cpu.accept_interrupt(registers, memory, 0x6060)
        advance(cpu, 0x3D13)
        gap_load_writes = memory.check_gap_loads()
        assert {row['pc'] for row in gap_load_writes} == {0x3FEC}
        memory.watch_start = False
        engine = load_restored(engine_row, 0x4000)
        assert memory[0x5F5E] == mode
        memory.watch_engine = True
        archive_ports.enter_pressed = False
        cpu.set_tracer(archive_ports)
        cpu.run()
        assert registers[PC] == 0x4003 and registers[SP] == 0x6000
        requests = [*((40 + i, 0x58 + i, 0xC000) for i in range(4)),
                    (30, 0x5B, 0x7700), (39, 0x18, 0xC000), (39, 0x18, 0xD000)]
        loads = service_requests(cpu, requests, (basic, dos), advance=advance)
        advance(cpu, 0x4030)
        assert registers[IM] == 2 and registers[IFF] and registers[SP] == 0x6000
        gaps_at_frame_entry = memory.gap_lifetime()
        hashes = []
        for _ in range(32):
            registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
            assert cpu.accept_interrupt(registers, memory, 0x4048)
            advance(cpu, 0x4030)
            cpu.run()
            advance(cpu, 0x4030)
            hashes.append(sha256(memory.banks[7][:0x1800]).hexdigest())
        assert len(set(hashes)) > 1
        memory.watch_engine = False
        paging_writes = [dict(pc=pc, port=port, value=value, count=count)
                         for (pc, port, value), count in sorted(archive_ports.paging_writes.items())]
        forced_transfer = check_forced_transfer(cpu, advance)
        return dict(start=start, engine=engine, bank_frames=32, bank_gap_reads_before_engine=0,
                    bank_gap_load_writes=gap_load_writes, bank_gap_writes_after_load_before_engine=0,
                    start_fixed_accesses=memory.start_fixed_summary(),
                    engine_loads=loads, fighter_frames=32, fighter_distinct_bitmaps=len(set(hashes)),
                    fighter_bitmap_hashes=hashes, mode_at_both_entries=mode,
                    paging_writes=paging_writes, forced_transfer=forced_transfer,
                    bank_gaps_at_engine_frame_entry=gaps_at_frame_entry,
                    bank_gaps_after_32_engine_frames=memory.gap_lifetime(),
                    engine_file_key_reads=memory.check_engine_file_keys(),
                    uncertain_engine_accesses=memory.uncertain_summary(),
                    selection_at_enter=list(selection_at_enter),
                    engine_selection_reads=[dict(pc=pc, address=address, value=value, count=count)
                                            for (pc, address, value), count in sorted(memory.selection_reads.items())])

    return check_menu(basic, dos, system, mode, handoff=enter, bootstrap=bootstrap,
                      memory=HandoffMemory(mode)) | {'basic_bootstrap': bootstrap_report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    rom = model_rom_context(args.dos_rom)
    transfer_references = check_transfer_word_references()
    disk, entries = catalogue_fixture()
    profile = check_handoff(rom, disk, entries)
    changed = check_handoff(rom, disk, entries, change_selection=True)
    scorpion = check_handoff(rom, disk, entries, mode=1)
    assert profile['selection_at_enter'] == [0, 0, 3, 0]
    assert changed['selection_at_enter'] == [1, 0, 3, 0]
    atm = check_handoff(rom, disk, entries, mode=2)
    assert scorpion['selection_at_enter'] == atm['selection_at_enter'] == profile['selection_at_enter']
    assert {(row['pc'], row['value']) for row in scorpion['paging_writes'] if row['port'] == 0x1FFD} == {
        (pc, value) for pc in (0x6366, 0x4FD7) for value in (0, 0x10)}
    assert {row['value'] for row in atm['paging_writes'] if row['port'] == 0xFFF7} == {
        0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xFA, 0xFF}
    for observed in (scorpion, atm):
        assert not any(row['value'] & 0x40 for row in observed['paging_writes'] if row['port'] == 0x7FFD)
    stack_words = {
        0: (),
        1: ((0x4625, (0x4FD9,), (0x4FCF,)),),
        2: (
            (0x4621, (0x3D30,), (0x5002,)),
            (0x4623, (0x4FF0, 0x2A55), (0x4FE6, 0x4FFF)),
            (0x4625, (0x4FFC,), (0x4FE5,)),
        ),
    }
    for observed in (profile, changed, scorpion, atm):
        assert observed['engine_selection_reads'] == [
            dict(pc=0x4012, address=0x5F5E, value=observed['mode_at_both_entries'], count=1)]
        assert observed['fighter_bitmap_hashes'] == profile['fighter_bitmap_hashes']
        assert observed['engine_loads'] == profile['engine_loads']
        gaps_at_entry = observed['bank_gaps_at_engine_frame_entry']
        gaps_after_frames = observed['bank_gaps_after_32_engine_frames']
        assert not any(row['reads_before_overwrite'] or row['reads_after_overwrite'] for row in gaps_at_entry)
        assert sum(row['overwritten_bytes'] for row in gaps_at_entry) == 4962
        assert not any(row['reads_before_overwrite'] for row in gaps_after_frames)
        assert [row['reads_after_overwrite'] for row in gaps_after_frames] == [0, 0, 0, 0, 0, 2304]
        assert gaps_after_frames[-1]['read_sites_after_overwrite'] == {0x472C: 2304}
        accesses = [item for region in observed['uncertain_engine_accesses'] for item in region['accesses']]
        expected = []
        # Два переключения страницы на каждом из 32 IRQ.
        for address, reads, writes in stack_words[observed['mode_at_both_entries']]:
            for kind, sites in (('read', reads), ('write', writes)):
                expected.extend((kind, pc, byte, 64) for pc in sites for byte in (address, address + 1))
        actual = [(item['kind'], item['pc'], item['address'], item['count']) for item in accesses]
        assert sorted(actual) == sorted(expected), (observed['mode_at_both_entries'], actual)
    extract_archive_rows(entries)
    result = dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom_sha256=sha256(rom[1]).hexdigest(),
                  catalogue_residue=check_catalogue_residue(), disabled_catalogue_entries=entries,
                  profile=profile, changed_bank_selection_profile=changed,
                  scorpion_profile=scorpion, atm_profile=atm,
                  transfer_references=transfer_references,
                  first_32_fighter_bitmaps_match_between_profiles=True,
                  first_characters_restored_only_in_model=True,
                  active_awaken_entry_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveMenuHandoffVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Четыре архивных файла извлечены. Модель исполнила цепочку BASIC, RUN, START и ENGINE через ROM TR-DOS.')


if __name__ == '__main__':
    main()
