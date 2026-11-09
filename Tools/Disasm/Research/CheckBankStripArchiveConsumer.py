"""Проверка загрузчика и рисователя BANK из внекаталожных секторов TRD."""
from collections import Counter
import hashlib
import json

from BankScreenStrips import all_tables, screen_position
from CheckInsetFrame import bitmap_address
from CheckStationFlightCycle import DISK, DISK_DIR, ENTRIES, payload, put, run_to
from TraceFlight import A, C, H, IFF, L, PC, SP, T, ROOT, Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import IM, get_registers


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

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and 0xDB4E <= address < 0xE21E:
            page = (self.o7ffd & 7) | ((self.o7ffd & 0x40) >> 3)
            bounds = self.gap_ranges.get(page)
            if bounds and bounds[0] <= address < bounds[1]:
                self.gap_reads[page, address] += 1
                self.gap_read_sites[page, self.cpu.registers[PC]] += 1
        return value

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

    def write_port(self, registers, port, value, offset):
        if port != 0x7FFD:
            assert port & 255 == 0xFE
            return
        self.pages.append(value)
        self.memory.out7ffd(value)

    def read_port(self, registers, port):
        return 254 if self.enter_pressed and port == 0xBFFE else 255


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


def expected_screen(data, start, initial):
    address = int.from_bytes(data[start:start + 2], 'little')
    column, y = screen_position(address)
    height = data[start + 2]
    expected = bytearray(initial)
    for line in range(height):
        destination = bitmap_address(y + line, column) - 0x4000
        source = start + 3 + 6 * line
        expected[destination:destination + 6] = data[source:source + 6]
    return expected, 6 * height


def check_renderer(cpu, files, ports):
    memory = cpu.memory
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
        memory[0x664B] = index % 4
        start_call(cpu, 0xC1D2, AF=(index // 4) << 8, HL=0x664B, DE=0x610E)
        run_to(cpu, RETURN_SENTINEL)
        assert bytes(memory[0x610E:0x6140]) == route and cpu.registers[SP] == 0xBFFE
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
            expected_direct, direct_bytes = expected_screen(data, direct, initial)
            expected_staged, staged_bytes = expected_screen(data, staged, initial)

            memory[0x610C] = (frame - 1) & 255
            memory[0x6063] = memory[0x664A] = 0
            ports.pages.clear()
            start_call(cpu, 0x6062)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x50 + slot - 33, 0x10]
            staged_data = data[staged:staged + 600]
            rom_bytes = 600 - len(staged_data)
            assert bytes(memory[0x67D7:0x6A2F]) == staged_data + bytes(memory[0:rom_bytes])
            if rom_bytes:
                wrapped_staging.append(dict(slot=slot, frame=frame, source=0xC000 + staged, rom_bytes=rom_bytes))
            assert memory[0x6063] == 1 and memory[0x610C] == frame

            # Проверка байтов, которые LDIR берёт за концом растра полосы.
            page = 8 + slot - 33
            gap = memory.gap_ranges.get(page)
            tail = None
            if gap:
                begin = max(staged, gap[0] - 0xC000)
                end = min(staged + 600, gap[1] - 0xC000)
                if begin < end:
                    assert begin >= staged + 3 + staged_bytes
                    first_copy = 0x67D7 + begin - staged
                    last_copy = first_copy + end - begin
                    tail = first_copy, last_copy, bytes(memory[first_copy:last_copy])

            ports.pages.clear()
            start_call(cpu, 0x659D)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x17] and cpu.registers[SP] == 0xBFFE
            assert memory.banks[7][:0x1B00] == expected_staged, (index, frame, staged_strip)
            if tail:
                first_copy, last_copy, original_tail = tail
                assert original_tail == data[begin:end]
                put(memory, first_copy, bytes(value ^ 255 for value in original_tail))
                memory.banks[7][:0x1B00] = initial
                ports.pages.clear()
                start_call(cpu, 0x659D)
                run_to(cpu, RETURN_SENTINEL)
                assert ports.pages == [0x17] and cpu.registers[SP] == 0xBFFE
                assert memory.banks[7][:0x1B00] == expected_staged
                put(memory, first_copy, original_tail)
                staged_tail_checks.append(dict(slot=slot, route=index, frame=frame,
                                               start=begin, end_exclusive=end,
                                               staged_address=first_copy, bytes=end - begin))

            ports.pages.clear()
            start_call(cpu, 0x65B0)
            run_to(cpu, RETURN_SENTINEL)
            assert ports.pages == [0x50 + slot - 33] and cpu.registers[SP] == 0xBFFE
            assert bytes(memory[0x4000:0x5B00]) == expected_direct, (index, frame, direct_strip)
            assert memory.banks[7][:0x1B00] == expected_staged and memory[0x6063] == 0
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


def check_archive_start():
    memory = ExtendedMemory()
    fixed = DISK[FIXED_OFFSET:BANK_OFFSET]
    assert len(fixed) == 0x6000
    put(memory, 0x6000, fixed)
    put(memory, 0xC000, DISK[BANK_OFFSET:BANK_OFFSET + 0x4000])
    cpu = Simulator(memory, {'PC': 0x6000})
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    registers = cpu.registers
    loads = []
    for slot, page in zip(range(31, 39), (0x15, 0x1F, *range(0x58, 0x5E))):
        run_to(cpu, 0x3D13)
        key = bytes(memory[0x5CDD:0x5CE6])
        assert key == DISK[16 * slot:16 * slot + 9]
        assert (registers[A], registers[C], registers[H], registers[L]) == (255, 0x0E, 0xC0, 0)
        assert memory.o7ffd == page
        data = payload(slot)
        put(memory, 0xC000, data)
        sp = registers[SP]
        registers[PC] = int.from_bytes(memory[sp:sp + 2], 'little')
        registers[SP] += 2
        loads.append(dict(slot=slot, key=key.decode('ascii'), port_value=page, size=len(data)))
    run_to(cpu, 0x6053)
    assert registers[SP] == 0x6000 and registers[IFF] and memory.o7ffd == 0x18
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
    return dict(loads=loads, initial_halt=0x6053, interrupt_handler=0x67A4, generated_branch=0x885C,
                fixed_bytes_loaded=len(fixed), complete_frame_cycles=len(frames), frames=frames,
                gap_reads=memory.gap_read_summary(),
                interrupts_scheduled_at_loop_boundaries=True,
                enter_request=dict(key=key.decode('ascii'), destination=0x4000, catalogued=False,
                                   stopped_at_trdos=0x3D13))


def main():
    manifest = json.loads((DISK_DIR / 'Manifest.json').read_bytes())
    component = next(row for row in manifest['components'] if '/Unallocated/' in row['path'])
    assert component['offset'] <= FIXED_OFFSET < BANK_OFFSET < component['offset'] + component['size']
    assert (ROOT / component['path']).read_bytes() == DISK[component['offset']:]
    files = {slot: payload(slot) for slot in SLOTS}
    memory = ExtendedMemory()
    put(memory, 0x6000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1000])
    put(memory, 0xC000, DISK[BANK_OFFSET:BANK_OFFSET + 0x4000])
    cpu = Simulator(memory)
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    keys = load_banks(cpu, files, ports)
    tables, distinct_strips, copied, wrapped_staging, staged_tails = check_renderer(cpu, files, ports)
    uses = Counter(table['slot'] for table in tables)
    assert uses == dict.fromkeys(SLOTS, 2)
    matches = check_gap_copies(files, component)
    gap_reads = memory.gap_read_summary()
    assert len(staged_tails) == 6 and sum(tail['bytes'] for tail in staged_tails) == 528
    for tail in staged_tails:
        summary = next(row for row in gap_reads if row['page'] == 8 + tail['slot'] - 33)
        assert summary['read_spans'] == [[0xC000 + tail['start'], 0xC000 + tail['end_exclusive']]]
        assert summary['read_sites'] == {'608E': tail['bytes']}
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(),
                  fixed_code_disk_offset=FIXED_OFFSET, bank_code_disk_offset=BANK_OFFSET,
                  trdos_file_keys=keys, tables=tables, distinct_drawn_strips=distinct_strips,
                  strip_draws=sum(2 * len(table['strip_pairs']) for table in tables),
                  bytes_drawn=copied, wrapped_staging=wrapped_staging, gap_copies=matches,
                  gap_reads_in_all_routes=gap_reads, staging_tail_checks=staged_tails,
                  original_start=check_archive_start(),
                  active_game_entry_proved=False,
                  trdos_substituted=True, machine_paging_model=True, native_execution=False,
                  assembly_executed=False)
    path = ROOT / 'Tools/Disasm/Reports/BankStripArchiveConsumerVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"{len(keys)} загрузок BANK, {len(tables)} таблиц, {result['strip_draws']} кадров, "
          f"{distinct_strips} разных полос, {copied} байтов растра, {len(matches)} совпадающих участков")


if __name__ == '__main__':
    main()
