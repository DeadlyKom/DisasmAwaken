"""Проверка загрузчика и рисователя BANK из внекаталожных секторов TRD."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

from BankScreenStrips import all_tables, screen_position
from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckControlsLegacySectorRead import run_with_rom
from CheckInsetFrame import bitmap_address
from CheckStationFlightCycle import DISK, DISK_DIR, ENTRIES, payload, put, run_to
from TraceFlight import A, C, H, IFF, L, PC, SP, T, ROOT, Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import IM, IXh, IXl, get_registers


FIXED_OFFSET = 0x8C200
BANK_OFFSET = 0x92200
SLOTS = range(33, 39)
RETURN_SENTINEL = 0x3FFF
GAP_COPY_RANGES = ((33, 0x1C92, 0x1DF8, 27), (34, 0x1CFE, 0x1E76, 0),
                   (35, 0x1CB6, 0x1EDA, 0), (37, 0x1B4E, 0x1FA2, 0),
                   (38, 0x1D16, 0x2006, 0))


class ExtendedMemory(SliceableMemory):
    """Модель селектора 63AE, перенос бита 3 на бит 6 порта 7FFD."""

    def __init__(self):
        super().__init__([bytearray(0x4000) for _ in range(16)], out7ffd=0x10)
        self.gap_ranges = {8 + slot - 33: (0xC000 + begin, 0xC000 + end)
                           for slot, begin, end, _ in GAP_COPY_RANGES}
        self.gap_ranges[11] = (0xDB66, 0xE21E)
        self.gap_ranges[0] = (0xDBAB, 0xDE6F)
        self.gap_reads = Counter()
        self.gap_read_sites = Counter()
        source_map = json.loads((ROOT / 'Tools/Disasm/Reports/SourceMap.json').read_bytes())
        bank_gaps = [row for row in source_map if row['slot'] in SLOTS and row['kind'] == 'unclassified']
        assert len(bank_gaps) == len(SLOTS)
        self.unclassified_ranges = {
            8 + row['slot'] - 33: (0xC000 + row['offset'], 0xC000 + row['offset'] + row['length'])
            for row in bank_gaps
        }
        assert len(self.unclassified_ranges) == len(SLOTS)
        self.read_watch_end = max(end for _, end in (*self.gap_ranges.values(), *self.unclassified_ranges.values()))
        self.unclassified_reads = Counter()
        self.unclassified_writes = Counter()
        self.unclassified_write_sites = Counter()

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and 0xDB4E <= address < self.read_watch_end:
            page = (self.o7ffd & 7) | ((self.o7ffd & 0x40) >> 3)
            bounds = self.gap_ranges.get(page)
            if bounds and bounds[0] <= address < bounds[1]:
                self.gap_reads[page, address] += 1
                self.gap_read_sites[page, self.cpu.registers[PC]] += 1
            bounds = self.unclassified_ranges.get(page)
            if bounds and bounds[0] <= address < bounds[1]:
                self.unclassified_reads[page, address] += 1
        return value

    def __setitem__(self, address, value):
        super().__setitem__(address, value)
        if 0xDB4E <= address < self.read_watch_end:
            page = (self.o7ffd & 7) | ((self.o7ffd & 0x40) >> 3)
            bounds = self.unclassified_ranges.get(page)
            if bounds and bounds[0] <= address < bounds[1]:
                self.unclassified_writes[page, address] += 1
                self.unclassified_write_sites[page, self.cpu.registers[PC]] += 1

    def check_gap_loads(self):
        expected = {(page, address): 1 for page, (begin, end) in self.unclassified_ranges.items()
                    for address in range(begin, end)}
        assert self.unclassified_writes == expected
        assert not self.unclassified_reads
        return [dict(page=page, pc=pc, writes=count)
                for (page, pc), count in sorted(self.unclassified_write_sites.items())]

    def gap_read_summary(self):
        summaries = []
        for page, (begin, end) in sorted(self.gap_ranges.items()):
            addresses = sorted(address for p, address in self.gap_reads if p == page)
            spans = []
            for address in addresses:
                if spans and spans[-1][1] == address:
                    spans[-1][1] += 1
                else:
                    spans.append([address, address + 1])
            sites = {f'{pc:04X}': count for (p, pc), count in self.gap_read_sites.items() if p == page}
            summaries.append(dict(page=page, start=begin, end_exclusive=end, read_spans=spans,
                                  distinct_addresses=len(addresses),
                                  total_reads=sum(sites.values()), read_sites=sites))
        return summaries

    def out7ffd(self, value):
        super().out7ffd(value)
        self.memory[3] = self.banks[(value & 7) | ((value & 0x40) >> 3)]


class ArchivePorts:
    def __init__(self, memory):
        self.memory = memory
        self.pages = []
        self.enter_pressed = False
        self.menu_key = None

    def write_port(self, registers, port, value, offset):
        if port != 0x7FFD:
            assert port & 255 == 0xFE
            return
        self.pages.append(value)
        self.memory.out7ffd(value)

    def read_port(self, registers, port):
        if self.enter_pressed and port == 0xBFFE:
            return 254
        if self.menu_key and port == self.menu_key[0]:
            return 255 ^ self.menu_key[1]
        return 255


def start_call(cpu, address, **pairs):
    cpu.registers[:] = get_registers(dict(pairs, PC=address, SP=0xBFFC), None, False)
    put(cpu.memory, 0xBFFC, RETURN_SENTINEL.to_bytes(2, 'little'))


def load_banks(cpu, files, ports):
    memory, registers = cpu.memory, cpu.registers
    assert bytes(memory[0xC369:0xC36F]) == bytes.fromhex('AE 63 5B 63 7E 63')
    put(memory, 0x6359, memory[0xC369:0xC36B])
    start_call(cpu, 0x6520)
    keys = []
    for slot, data in files.items():
        run_to(cpu, 0x3D13)
        assert (registers[A], registers[C], registers[H], registers[L]) == (255, 0x0E, 0xC0, 0)
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9] == f'BANK{slot - 33}   C'.encode('ascii')
        assert len(data) == 0x4000 and ENTRIES[slot]['parameter'] == 0xC000
        assert memory.o7ffd == 0x50 + slot - 33
        put(memory, 0xC000, data)
        sp = registers[SP]
        registers[PC] = int.from_bytes(memory[sp:sp + 2], 'little')
        registers[SP] += 2
        assert registers[PC] == 0x6551
        keys.append(key.decode('ascii'))
    run_to(cpu, RETURN_SENTINEL)
    assert registers[SP] == 0xBFFE and ports.pages == list(range(0x50, 0x56))
    for slot, data in files.items():
        assert memory.banks[8 + slot - 33] == data
    return keys


def load_rom_file(cpu, ports, roms, continuation, slot, raw):
    memory = cpu.memory
    basic, dos = roms
    start = len(ports.read_destinations)
    memory.memory[0] = basic

    def set_rom(image):
        memory.memory[0] = image

    run_with_rom(cpu, basic, dos, set_rom, continuation)
    file_reads = [(sector, address) for sector, address in ports.read_destinations[start:] if sector[0]]
    entry = ENTRIES[slot]
    first = entry['offset'] // 256
    full, tail = divmod(len(raw), 256)
    assert entry['sector_count'] == full + bool(tail)
    targets = [0xC000 + 256 * i for i in range(full)] + [0x5D25]
    expected_reads = [(divmod(index, 16), address) for index, address in enumerate(targets, first)]
    assert file_reads == [((track, sector + 1), address) for (track, sector), address in expected_reads]
    assert bytes(memory[0xC000:0xC000 + len(raw)]) == raw
    return file_reads[-1][0], file_reads[-1][1]


def check_rom_loads(files, rom_profile):
    basic, dos, sysvars = rom_profile
    memory = ExtendedMemory()
    put(memory, 0x6000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1000])
    put(memory, 0xC000, DISK[BANK_OFFSET:BANK_OFFSET + 0x4000])
    put(memory, 0x5C00, sysvars)
    memory[0x5D06] = 9
    cpu = Simulator(memory)
    memory.cpu = cpu
    archive_ports = ArchivePorts(memory)
    cpu.set_tracer(archive_ports)
    put(memory, 0x6359, memory[0xC369:0xC36B])
    start_call(cpu, 0x6520, IY=0x5C3A)
    disk_ports = BasicReadPorts(memory)
    result = []

    for slot, raw in files.items():
        run_to(cpu, 0x3D13)
        bank = 8 + slot - 33
        assert memory.o7ffd == 0x50 + slot - 33
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9]
        cpu.set_tracer(disk_ports)
        assert len(raw) == 0x4000
        extra_sector, extra_destination = load_rom_file(cpu, disk_ports, (basic, dos), 0x6551, slot, raw)
        assert memory.banks[bank] == raw
        result.append(dict(slot=slot, key=key.decode('ascii'), page=bank, loaded_bytes=len(raw),
                           extra_sector=extra_sector, extra_sector_destination=extra_destination))
        cpu.set_tracer(archive_ports)
    run_to(cpu, RETURN_SENTINEL)
    assert cpu.registers[SP] == 0xBFFE and archive_ports.pages == list(range(0x50, 0x56))
    for slot, raw in files.items():
        assert memory.banks[8 + slot - 33] == raw
    return dict(profiles=result, dos_rom_sha256=hashlib.sha256(dos).hexdigest(), trdos_substituted=False,
                gap_load_writes=memory.check_gap_loads())


def expected_screen(data, start, initial, *, right=False):
    address = int.from_bytes(data[start:start + 2], 'little')
    if right:
        address = (address & 0xFF00) | ((address + 31) & 255)
    column, y = screen_position(address)
    height = data[start + 2]
    expected = bytearray(initial)
    for line in range(height):
        destination = bitmap_address(y + line, column) - 0x4000
        source = start + 3 + 6 * line
        row = data[source:source + 6]
        if right:
            expected[destination - 5:destination + 1] = bytes(int(f'{value:08b}'[::-1], 2) for value in reversed(row))
        else:
            expected[destination:destination + 6] = row
    return expected, 6 * height


def check_renderer(cpu, files, ports, *, right=False):
    memory = cpu.memory
    route_address = 0x6140 if right else 0x610E
    selector_address = 0x664D if right else 0x664B
    index_address = 0x610D if right else 0x610C
    stage = 0x609C if right else 0x6062
    ready_address = stage + 1
    buffer = 0x6A2F if right else 0x67D7
    draw_staged = 0x65E9 if right else 0x659D
    draw_direct = 0x65FC if right else 0x65B0
    strip_indices = {(table['slot'], row['start']): row['index']
                     for table in all_tables(files) for row in table['rows']}
    tables = []
    used = set()
    copied = 0
    wrapped_staging = []
    staged_tail_checks = []
    for index in range(12):
        memory.out7ffd(0x10)
        pointer = int.from_bytes(memory[0xC1E7 + 2 * index:0xC1E9 + 2 * index], 'little')
        route = bytes(memory[pointer:pointer + 50])
        slot = 33 + route[0]
        memory[selector_address] = index % 4
        start_call(cpu, 0xC1D2, AF=(index // 4) << 8, HL=selector_address, DE=route_address)
        run_to(cpu, RETURN_SENTINEL)
        assert bytes(memory[route_address:route_address + 50]) == route and cpu.registers[SP] == 0xBFFE
        strip_count = route[1]
        assert 0 < strip_count <= 12
        selected = []
        for frame in range(strip_count):
            staged = int.from_bytes(route[2 + 2 * frame:4 + 2 * frame], 'little') - 0xC000
            direct = int.from_bytes(route[26 + 2 * frame:28 + 2 * frame], 'little') - 0xC000
            staged_strip, direct_strip = strip_indices[slot, staged], strip_indices[slot, direct]
            assert direct_strip % 2 == 0 and staged_strip == direct_strip + 1
            used.update(((slot, direct_strip), (slot, staged_strip)))
            selected.append([direct_strip, staged_strip])
            data = files[slot]
            initial = bytes((address ^ index ^ frame) & 255 for address in range(0x1B00))
            put(memory, 0x4000, initial)
            memory.banks[7][:0x1B00] = initial
            expected_direct, direct_bytes = expected_screen(data, direct, initial, right=right)
            expected_staged, staged_bytes = expected_screen(data, staged, initial, right=right)

            memory[index_address] = strip_count - 1 if right and frame == 0 else (frame - 1) & 255
            memory[ready_address] = memory[0x664A] = 0
            ports.pages.clear()
            start_call(cpu, stage)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x50 + slot - 33, 0x10]
            staged_data = data[staged:staged + 600]
            rom_bytes = 600 - len(staged_data)
            expected_buffer = staged_data + bytes(memory[0:rom_bytes])
            assert bytes(memory[buffer:buffer + 600]) == expected_buffer
            if rom_bytes:
                wrapped_staging.append(dict(slot=slot, frame=frame, source=0xC000 + staged, rom_bytes=rom_bytes))
            assert memory[ready_address] == 1 and memory[index_address] == frame
            if right:
                ports.pages.clear()
                start_call(cpu, stage)
                run_to(cpu, RETURN_SENTINEL)
                assert not ports.pages and memory[index_address] == frame and memory[ready_address] == 1
                assert bytes(memory[buffer:buffer + 600]) == expected_buffer

            # Проверка байтов, которые LDIR берёт за концом растра полосы.
            page = 8 + slot - 33
            gap = memory.gap_ranges.get(page)
            tail = None
            if gap:
                begin = max(staged, gap[0] - 0xC000)
                end = min(staged + 600, gap[1] - 0xC000)
                if begin < end:
                    assert begin >= staged + 3 + staged_bytes
                    first_copy = buffer + begin - staged
                    last_copy = first_copy + end - begin
                    tail = first_copy, last_copy, bytes(memory[first_copy:last_copy])

            ports.pages.clear()
            start_call(cpu, draw_staged)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x17] and cpu.registers[SP] == 0xBFFE
            assert memory.banks[7][:0x1B00] == expected_staged, (index, frame, staged_strip)
            if tail:
                first_copy, last_copy, original_tail = tail
                assert original_tail == data[begin:end]
                put(memory, first_copy, bytes(value ^ 255 for value in original_tail))
                memory.banks[7][:0x1B00] = initial
                ports.pages.clear()
                start_call(cpu, draw_staged)
                run_to(cpu, RETURN_SENTINEL)
                assert ports.pages == [0x17] and cpu.registers[SP] == 0xBFFE
                assert memory.banks[7][:0x1B00] == expected_staged
                put(memory, first_copy, original_tail)
                staged_tail_checks.append(dict(slot=slot, route=index, frame=frame,
                                               start=begin, end_exclusive=end,
                                               staged_address=first_copy, bytes=end - begin))

            ports.pages.clear()
            start_call(cpu, draw_direct)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x50 + slot - 33] and cpu.registers[SP] == 0xBFFE
            assert bytes(memory[0x4000:0x5B00]) == expected_direct, (index, frame, direct_strip)
            assert memory.banks[7][:0x1B00] == expected_staged and memory[ready_address] == 0
            copied += direct_bytes + staged_bytes
        tables.append(dict(index=index, table_address=pointer, slot=slot, strip_pairs=selected))
    return tables, len(used), copied, wrapped_staging, staged_tail_checks


def check_gap_copies(files, component):
    results = []
    for slot, start, end, shift in GAP_COPY_RANGES:
        disk_start = BANK_OFFSET + 0x5D + start + shift
        disk_end = disk_start + end - start
        assert component['offset'] <= disk_start < disk_end <= component['offset'] + component['size']
        data = files[slot][start:end]
        assert data == DISK[disk_start:disk_end] and len(set(data)) > 16
        assert files[slot][end] != DISK[disk_end]
        results.append(dict(slot=slot, start=start, end=end, length=len(data), disk_offset=disk_start,
                            nonzero_bytes=len(data) - data.count(0)))
    return results


def check_menu_tile_keys(cpu, ports):
    memory, registers = cpu.memory, cpu.registers
    profiles = (
        (0xFDFE, 4, 0x664B, 1, 0xC026, 0xC1A4),
        (0xFDFE, 1, 0x664B, -1, 0xC026, 0xC1A4),
        (0xFDFE, 2, 0x664C, 1, 0xC026, 0xC1A4),
        (0xFBFE, 2, 0x664C, -1, 0xC026, 0xC1A4),
        (0xDFFE, 16, 0x664D, -1, 0xC004, 0xC176),
        (0xDFFE, 4, 0x664D, 1, 0xC004, 0xC176),
        (0xDFFE, 8, 0x664E, 1, 0xC004, 0xC176),
        (0xEFFE, 8, 0x664E, -1, 0xC004, 0xC176),
    )
    # Проверка равных селекторов через те же клавиши, затем возврат к начальному выбору.
    profiles += (profiles[0],) * 3 + (profiles[4], profiles[5]) + (profiles[1],) * 3

    def tick(observe):
        assert registers[PC] == 0x6054 and registers[IFF]
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        assert cpu.accept_interrupt(registers, memory, 0x6060)
        run_to(cpu, 0x6054, observe)
        cpu.run()
        run_to(cpu, 0x6054, observe)
        assert registers[SP] == 0x6000

    result = []
    for row, mask, address, delta, redraw, commit in profiles:
        initial = bytes(memory[0x664B:0x664F])
        expected = bytearray(initial)
        expected[address - 0x664B] += delta
        same_selection = initial[:2] == initial[2:]
        observed = Counter()
        redraw_branches = Counter()
        redrawing = False

        def observe(pc):
            nonlocal redrawing
            if pc in (redraw, commit, 0x632C, 0x633E):
                assert memory.o7ffd & 7 == 0
                observed[pc] += 1
            if pc == redraw:
                redrawing = True
            elif pc == 0x632D:
                redrawing = False
            if redrawing and pc in (0xC09E, 0xC126, 0xC13F, 0xC295):
                redraw_branches[pc] += 1

        ports.menu_key = (row, mask)
        for frames in range(1, 9):
            tick(observe)
            if bytes(memory[0x664B:0x664F]) != initial:
                break
        else:
            raise AssertionError((row, mask, 'селектор не изменён'))
        assert bytes(memory[0x664B:0x664F]) == expected
        assert observed == dict.fromkeys((redraw, commit, 0x632C, 0x633E), 1)
        assert redraw_branches == ({0xC09E: 1, 0xC126: 3, 0xC295: 1} if same_selection else {0xC13F: 3})
        result.append(dict(row=row, mask=mask, frames_until_change=frames,
                           selection_before=list(initial), selection_after=list(expected),
                           redraw=redraw, commit=commit, equal_selections_on_redraw=same_selection,
                           redraw_branches={f'{pc:04X}': count for pc, count in redraw_branches.items()}))
        ports.menu_key = None
        for _ in range(4):
            tick(lambda pc: None)
    assert result[0]['selection_before'] == result[-1]['selection_after']
    assert {row['redraw'] for row in result if row['equal_selections_on_redraw']} == {0xC004, 0xC026}
    return result


def check_all_selector_transitions(source_cpu):
    memory = ExtendedMemory()
    for bank, source in zip(memory.banks, source_cpu.memory.banks, strict=True):
        bank[:] = source
    memory.roms = source_cpu.memory.roms
    memory.out7ffd(source_cpu.memory.o7ffd)
    memory.memory[0] = source_cpu.memory.memory[0]
    cpu = Simulator(memory)
    memory.cpu = cpu
    cpu.set_tracer(ArchivePorts(memory))
    registers = cpu.registers
    limits = (3, 2, 3, 2)
    states = set(product(*(range(limit + 1) for limit in limits)))
    start = tuple(memory[0x664B:0x664F])
    assert start in states
    graph = {state: [] for state in states}
    for state in states:
        for axis, limit in enumerate(limits):
            for step in (1, -1):
                value = state[axis] + step
                if 0 <= value <= limit:
                    target = state[:axis] + (value,) + state[axis + 1:]
                    graph[state].append((target, axis * 2 + (step < 0)))

    # Замкнутый обход ориентированных рёбер, каждый допустимый шаг исполняется один раз.
    stack, reverse_walk = [(start, None)], []
    while stack:
        state, _ = stack[-1]
        if graph[state]:
            stack.append(graph[state].pop())
        else:
            reverse_walk.append(stack.pop())
    assert len(reverse_walk) == 817 and reverse_walk[0][0] == start

    def call_selector(key, *, fresh):
        address = 0x6297 + key * 12
        raw = bytes(memory[address:address + 12])
        latch = int.from_bytes(raw[2:4], 'little')
        assert int.from_bytes(raw[4:6], 'little') == 0x664B + key // 2
        if fresh:
            memory[latch] = 0
        registers[IXh], registers[IXl] = divmod(address, 256)
        registers[PC], registers[SP] = 0x62F8, 0x5FFE
        put(memory, 0x5FFE, RETURN_SENTINEL.to_bytes(2, 'little'))
        run_to(cpu, RETURN_SENTINEL)
        assert registers[SP] == 0x6000 and memory[latch] == raw[0]
        assert memory.o7ffd & 7 == 0

    route_bank = DISK[BANK_OFFSET:BANK_OFFSET + 0x4000]
    original_routes = []
    for index in range(12):
        entry = 0x1E7 + 2 * index
        offset = int.from_bytes(route_bank[entry:entry + 2], 'little') - 0xC000
        original_routes.append(route_bank[offset:offset + 50])
    assert all(len(route) == 50 for route in original_routes)

    def assert_routes(state):
        for side, destination in enumerate((0x610E, 0x6140)):
            minor, major = state[side * 2:side * 2 + 2]
            assert bytes(memory[destination:destination + 50]) == original_routes[major * 4 + minor]

    used, visited = set(), set()
    current = start
    bounds = 0
    assert_routes(start)
    for target, key in reversed(reverse_walk):
        if key is not None:
            assert (current, target) not in used
            used.add((current, target))
            call_selector(key, fresh=True)
            assert tuple(memory[0x664B:0x664F]) == target
            assert_routes(target)
            call_selector(key, fresh=False)
            assert tuple(memory[0x664B:0x664F]) == target
        if target not in visited:
            for axis, limit in enumerate(limits):
                for step, border in ((1, limit), (-1, 0)):
                    if target[axis] == border:
                        call_selector(2 * axis + (step < 0), fresh=True)
                        assert tuple(memory[0x664B:0x664F]) == target
                        assert_routes(target)
                        bounds += 1
            visited.add(target)
        current = target
    assert visited == states and len(used) == 816 and current == start and bounds == 336
    assert not memory.unclassified_reads and not memory.unclassified_writes
    for page, (begin, end) in memory.unclassified_ranges.items():
        assert memory.banks[page][begin - 0xC000:end - 0xC000] == source_cpu.memory.banks[page][begin - 0xC000:end - 0xC000]
    return dict(states=len(visited), directed_steps=len(used), held_steps_blocked=len(used),
                boundary_steps_blocked=bounds, starts_and_ends_at=list(start),
                both_route_descriptors_compared=True, bank_gaps_preserved=True, bank_gap_reads=0, bank_gap_writes=0,
                prepared_key_records=True, irq_executed_during_walk=False)


def check_archive_start(rom_profile=None):
    memory = ExtendedMemory()
    fixed = DISK[FIXED_OFFSET:BANK_OFFSET]
    assert len(fixed) == 0x6000
    put(memory, 0x6000, fixed)
    put(memory, 0xC000, DISK[BANK_OFFSET:BANK_OFFSET + 0x4000])
    if rom_profile is not None:
        put(memory, 0x5C00, rom_profile[2])
        memory[0x5D06] = 9
    cpu = Simulator(memory, {'PC': 0x6000, 'IY': 0x5C3A})
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    registers = cpu.registers
    loads = []
    disk_ports = BasicReadPorts(memory) if rom_profile is not None else None
    for slot, page in zip(range(31, 39), (0x15, 0x1F, *range(0x58, 0x5E))):
        run_to(cpu, 0x3D13)
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9]
        assert (registers[A], registers[C], registers[H], registers[L]) == (255, 0x0E, 0xC0, 0)
        assert memory.o7ffd == page
        data = payload(slot)
        sp = registers[SP]
        continuation = int.from_bytes(memory[sp:sp + 2], 'little')
        if rom_profile is None:
            put(memory, 0xC000, data)
            registers[PC] = continuation
            registers[SP] += 2
        else:
            cpu.set_tracer(disk_ports)
            load_rom_file(cpu, disk_ports, rom_profile[:2], continuation, slot, data)
            cpu.set_tracer(ports)
        loads.append(dict(slot=slot, key=key.decode('ascii'), port_value=page, size=len(data)))
    run_to(cpu, 0x6053)
    assert registers[SP] == 0x6000 and registers[IFF] and memory.o7ffd == 0x18
    gap_load_writes = memory.check_gap_loads()
    for slot, bank in ((31, 5), (32, 7)):
        assert memory.banks[bank][:0x1800] == payload(slot)[:0x1800]
        assert bytes(memory.banks[bank][0x1800:0x1B00]) == bytes([7]) * 768

    frames = []
    visited = set()
    for index in range(64):
        # Первый IRQ будит HALT, остальные подаются на границе цикла.
        assert registers[IFF]
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        if index == 0:
            cpu.run()
        previous = 0x6053 if index == 0 else 0x6060
        assert registers[PC] == 0x6054 and cpu.accept_interrupt(registers, memory, previous)
        assert registers[PC] == 0x5F5F
        run_to(cpu, 0x6054, visited.add)
        cpu.run()
        run_to(cpu, 0x6054)
        assert registers[SP] == 0x6000 and memory.o7ffd == (0x18 if index & 1 else 0x10)
        left, right = memory[0x610C], memory[0x610D]
        assert (left, right) == (((index + 1) // 4) % 7, ((index + 3) // 4) % 7)
        frames.append(dict(left=left, right=right, page=memory.o7ffd,
                           bitmap_sha256=[hashlib.sha256(memory.banks[bank][:0x1800]).hexdigest()
                                          for bank in (5, 7)]))
    assert {0x67A4, 0x6198, 0x657E, 0x885C} <= visited
    initial_gap_reads = memory.gap_read_summary()
    menu_keys = check_menu_tile_keys(cpu, ports)
    selector_transitions = check_all_selector_transitions(cpu) if rom_profile is not None else None
    # Проверка дисковой границы при выборе, отсутствующий файл не подменяется.
    ports.enter_pressed = True
    assert cpu.accept_interrupt(registers, memory, 0x6060)
    run_to(cpu, 0x3D13)
    key = bytes(memory[0x5CDD:0x5CE6])
    assert key == b'ENGINE  C'
    assert all(DISK[16 * slot:16 * slot + 9] != key for slot in ENTRIES)
    assert (registers[A], registers[C], registers[H], registers[L], registers[IM]) == (255, 0x0E, 0x40, 0, 1)
    sp = registers[SP]
    assert int.from_bytes(memory[sp:sp + 2], 'little') == 0x4000
    assert not memory.unclassified_reads
    engine = dict(key=key.decode('ascii'), destination=0x4000, catalogued=False, stopped_at_trdos=0x3D13)
    if rom_profile is not None:
        basic, dos, _ = rom_profile
        cpu.set_tracer(disk_ports)
        memory.memory[0] = basic

        def set_rom(image):
            memory.memory[0] = image

        before = bytes(memory[0x4000:0x5B00])
        cursor = len(disk_ports.attempts)
        try:
            run_with_rom(cpu, basic, dos, set_rom, 0x4000)
        except AssertionError as error:
            raise AssertionError(('ENGINE', hex(registers[PC]), memory[0x5D0F],
                                  disk_ports.attempts[cursor:])) from error
        sectors = disk_ports.attempts[cursor:]
        assert sectors == [(0, 1), (0, 2), (0, 3)] and memory[0x5D0F] == 1
        assert bytes(memory[0x4000:0x5B00]) == before
        engine.update(stopped_at_trdos=None, returned_to=registers[PC], sector_reads=sectors,
                      status=memory[0x5D0F], destination_prefix=before[:16].hex())
    assert memory.check_gap_loads() == gap_load_writes
    return dict(loads=loads, initial_halt=0x6053, interrupt_handler=0x67A4, generated_branch=0x885C,
                fixed_bytes_loaded=len(fixed), complete_frame_cycles=len(frames), frames=frames,
                gap_reads=initial_gap_reads, tile_menu_keys=menu_keys,
                selector_transitions=selector_transitions,
                gap_reads_after_menu_keys=memory.gap_read_summary(), unclassified_bank_reads=0,
                gap_load_writes=gap_load_writes, unclassified_bank_writes_after_load=0,
                interrupts_scheduled_at_loop_boundaries=True,
                enter_request=engine)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dos-rom', type=Path)
    args = parser.parse_args()
    manifest = json.loads((DISK_DIR / 'Manifest.json').read_bytes())
    component = next(row for row in manifest['components'] if '/Unallocated/' in row['path'])
    assert component['offset'] <= FIXED_OFFSET < BANK_OFFSET < component['offset'] + component['size']
    assert (ROOT / component['path']).read_bytes() == DISK[component['offset']:]
    bit_reverse = bytes(int(f'{value:08b}'[::-1], 2) for value in range(256))
    assert DISK[FIXED_OFFSET + 0x400:FIXED_OFFSET + 0x500] == bit_reverse
    files = {slot: payload(slot) for slot in SLOTS}
    memory = ExtendedMemory()
    put(memory, 0x6000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1000])
    put(memory, 0xC000, DISK[BANK_OFFSET:BANK_OFFSET + 0x4000])
    cpu = Simulator(memory)
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    keys = load_banks(cpu, files, ports)
    gap_load_writes = memory.check_gap_loads()
    tables, distinct_strips, copied, wrapped_staging, staged_tails = check_renderer(cpu, files, ports)
    uses = Counter(table['slot'] for table in tables)
    assert uses == dict.fromkeys(SLOTS, 2)
    matches = check_gap_copies(files, component)
    gap_reads = memory.gap_read_summary()
    assert len(staged_tails) == 6 and sum(tail['bytes'] for tail in staged_tails) == 528
    assert memory.check_gap_loads() == gap_load_writes
    unclassified = [
        dict(page=page, start=begin, end_exclusive=end, bytes=end - begin)
        for page, (begin, end) in sorted(memory.unclassified_ranges.items())
    ]
    for row in unclassified:
        data = files[row['page'] + 33 - 8]
        assert data[row['start'] - 0xC000:row['end_exclusive'] - 0xC000] == bytes(row['bytes'])
    for tail in staged_tails:
        summary = next(row for row in gap_reads if row['page'] == 8 + tail['slot'] - 33)
        assert summary['read_spans'] == [[0xC000 + tail['start'], 0xC000 + tail['end_exclusive']]]
        assert summary['read_sites'] == {'608E': tail['bytes']}
    memory.gap_reads.clear()
    memory.gap_read_sites.clear()
    right_tables, right_distinct, right_copied, right_wrapped, right_tails = check_renderer(cpu, files, ports, right=True)
    assert (right_tables, right_distinct, right_copied, right_wrapped) == (tables, distinct_strips, copied, wrapped_staging)
    assert len(right_tails) == 6 and sum(tail['bytes'] for tail in right_tails) == 528
    assert memory.check_gap_loads() == gap_load_writes
    right_reads = memory.gap_read_summary()
    for tail in right_tails:
        summary = next(row for row in right_reads if row['page'] == 8 + tail['slot'] - 33)
        assert summary['read_spans'] == [[0xC000 + tail['start'], 0xC000 + tail['end_exclusive']]]
        assert summary['read_sites'] == {'60C8': tail['bytes']}
    rom_profile = model_rom_context(args.dos_rom) if args.dos_rom else None
    archive_start = check_archive_start()
    real_start = None
    if rom_profile is not None:
        real_start = check_archive_start(rom_profile)
        assert real_start['frames'] == archive_start['frames']
        assert real_start['tile_menu_keys'] == archive_start['tile_menu_keys']
        real_start['frames_and_menu_match_stub_profile'] = True
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(),
                  fixed_code_disk_offset=FIXED_OFFSET, bank_code_disk_offset=BANK_OFFSET,
                  trdos_file_keys=keys, tables=tables, distinct_drawn_strips=distinct_strips,
                  strip_draws=sum(2 * len(table['strip_pairs']) for table in tables),
                  bytes_drawn=copied, wrapped_staging=wrapped_staging, gap_copies=matches,
                  gap_reads_in_all_routes=gap_reads, staging_tail_checks=staged_tails,
                  right_renderer=dict(strip_draws=sum(2 * len(table['strip_pairs']) for table in right_tables),
                                      distinct_drawn_strips=right_distinct, bytes_drawn=right_copied,
                                      read_sites=right_reads, staging_tail_checks=right_tails,
                                      mirror_lookup_bytes=len(bit_reverse), busy_buffer_and_frame_wrap_checked=True),
                  residual_unclassified_bank_ranges=unclassified, residual_unclassified_bank_reads_in_all_routes=0,
                  residual_unclassified_bank_writes_in_all_routes=0,
                  original_start=archive_start,
                  real_trdos_loads=check_rom_loads(files, rom_profile) if rom_profile is not None else None,
                  original_start_with_rom=real_start,
                  active_game_entry_proved=False,
                  trdos_substituted=True, machine_paging_model=True, native_execution=False,
                  assembly_executed=False)
    path = ROOT / 'Tools/Disasm/Reports/BankStripArchiveConsumerVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"{len(keys)} загрузок BANK, {len(tables)} таблиц, {result['strip_draws']} кадров, "
          f"{distinct_strips} разных полос, {copied} байтов растра, {len(matches)} совпадающих участков")


if __name__ == '__main__':
    main()
