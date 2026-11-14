"""Исходный загрузчик, разбиение и растровый цикл scene1po из свободных секторов."""
import argparse
import hashlib
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckControlsLegacySectorRead import run_with_rom
from CheckInsetFrame import bitmap_address
from CheckStationFlightCycle import DISK, ENTRIES, payload, put, run_to
from TraceFlight import A, C, H, L, PC, SP, ROOT, Simulator
from skoolkit.simutils import get_registers


FIXED_OFFSET = 0x8B100
SLOT = 30
RETURN_SENTINEL = 0x3FFF
ROW_BYTES = 92
HEIGHT = 203
INPUT = 0x7700


class SceneArchiveMemory(ExtendedMemory):
    scratch_writes = None
    background_reads = None

    def __getitem__(self, address):
        if self.background_reads is not None and isinstance(address, int) and address >= INPUT:
            self.background_reads.append(address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.scratch_writes is not None and 0x5D25 <= address < 0x5E25:
            self.scratch_writes.append((address, value))
        super().__setitem__(address, value)


def start_call(cpu, address, *, stack=0x5BFC, **pairs):
    cpu.registers[:] = get_registers(dict(pairs, PC=address, SP=stack), None, False)
    put(cpu.memory, stack, RETURN_SENTINEL.to_bytes(2, 'little'))


def check_background(cpu, ports, raw):
    """Сверяет полный вывод 4974 по раскладке ULA и исходным строкам ресурса."""
    memory = cpu.memory
    assert (memory[0x4A4F], memory[0x4A53]) == (58, 11)
    initial_bitmap = bytes((index * 37 + 91) & 255 for index in range(6912))
    rows = [(y, 0, 32) for y in range(191, 24, -1)]
    rows += [(y, 0, 32) for y in range(14, -1, -1)]
    rows += [(y, 15, 2) for y in range(24, 14, -1)]
    counts = sum(width for _, _, width in rows)
    assert counts == 5844
    addresses_read = set()
    for y in range(12):
        for x in range(59):
            memory.banks[7][:6912] = initial_bitmap
            memory[0x4A55] = y
            put(memory, 0x4A57, (INPUT + x).to_bytes(2, 'little'))
            wanted = bytearray(initial_bitmap)
            reads = []
            for line, column, width in rows:
                source = (y + 191 - line) * ROW_BYTES + x + column
                destination = bitmap_address(line) - 0x4000 + column
                wanted[destination:destination + width] = raw[source:source + width]
                reads.extend(range(INPUT + source, INPUT + source + width))
            start_call(cpu, 0x4974)
            ports.pages.clear()
            memory.background_reads = []
            cpu.run(start=0x4974, stop=RETURN_SENTINEL)
            if memory.background_reads != reads:
                mismatch = next((i for i, (actual, expected) in enumerate(zip(memory.background_reads, reads))
                                 if actual != expected), min(len(memory.background_reads), len(reads)))
                raise AssertionError((x, y, mismatch, len(memory.background_reads), len(reads),
                                      [hex(address) for address in memory.background_reads[mismatch:mismatch + 4]],
                                      [hex(address) for address in reads[mismatch:mismatch + 4]]))
            memory.background_reads = None
            assert memory.banks[7][:6912] == wanted, (x, y)
            assert ports.pages == [0x1F] and cpu.registers[SP] == 0x5BFE
            addresses_read.update(reads)
    assert addresses_read == {INPUT + row * ROW_BYTES + column
                              for row in range(HEIGHT) for column in range(90)}
    return dict(profiles=59 * 12, written_bitmap_bytes_per_profile=counts,
                fixed_source_first=min(addresses_read), fixed_source_last=max(addresses_read),
                distinct_source_bytes=len(addresses_read), all_reads_in_fixed_ram=True,
                source_row_visible_bytes=90, source_row_trailing_bytes_not_read=2,
                copied_page_13_or_14_read=False, intermediate_rows=[15, 24],
                intermediate_columns=[15, 16], untouched_bitmap_and_attributes_compared=True)


def exercise(include_sector_tail, rom_profile=None, *, check_full_background=False):
    raw = payload(SLOT)
    entry = ENTRIES[SLOT]
    assert len(raw) == ROW_BYTES * HEIGHT and entry['length'] == len(raw)
    sectors = DISK[entry['offset']:entry['offset'] + 0x4900]
    data = sectors if include_sector_tail else raw
    memory = SceneArchiveMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    assert int.from_bytes(memory[0x4A4B:0x4A4D], 'little') == ROW_BYTES
    assert int.from_bytes(memory[0x4A51:0x4A53], 'little') == HEIGHT
    assert bytes(memory[0x5018:0x501A]) == bytes.fromhex('B8 4F')
    put(memory, 0x4FB6, memory[0x5018:0x501A])
    cpu = Simulator(memory)
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    if rom_profile is not None:
        put(memory, 0x5C00, rom_profile[2])
        memory[0x5D06] = 9
        fixed_marker = bytes(range(0x91, 0x9D))
        put(memory, INPUT + len(raw), fixed_marker)
    start_call(cpu, 0x4916, IY=0x5C3A, stack=0x5FFD if rom_profile is not None else 0x5BFC)
    run_to(cpu, 0x3D13)
    key = bytes(memory[0x5CDD:0x5CE6])
    assert key == DISK[16 * SLOT:16 * SLOT + 9] == b'scene1pos'
    registers = cpu.registers
    assert (registers[A], registers[C], registers[H], registers[L]) == (255, 0x0E, 0x77, 0)
    file_reads = None
    if rom_profile is None:
        put(memory, INPUT, data)
        stack = registers[SP]
        registers[PC] = int.from_bytes(memory[stack:stack + 2], 'little')
        registers[SP] += 2
        assert registers[PC] == 0x492B
    else:
        basic, dos, _ = rom_profile
        disk_ports = BasicReadPorts(memory)
        cpu.set_tracer(disk_ports)

        def set_rom(image):
            memory.memory[0] = image

        set_rom(basic)
        memory.scratch_writes = []
        try:
            run_with_rom(cpu, basic, dos, set_rom, 0x492B)
        except AssertionError as error:
            raise AssertionError((hex(registers[PC]), disk_ports.attempts[-10:],
                                  disk_ports.read_destinations[-10:])) from error
        file_reads = [(sector, address) for sector, address in disk_ports.read_destinations if sector[0]]
        first = entry['offset'] // 256
        full_sectors, final_bytes = divmod(len(raw), 256)
        assert final_bytes == 244 and entry['sector_count'] == full_sectors + 1
        targets = [INPUT + 256 * i for i in range(full_sectors)] + [0x5D25]
        expected_reads = [(divmod(index, 16), address) for index, address in enumerate(targets, first)]
        assert file_reads == [((track, sector + 1), address) for (track, sector), address in expected_reads]
        assert bytes(memory[INPUT:INPUT + len(raw)]) == raw
        assert bytes(memory[INPUT + len(raw):0xC000]) == fixed_marker
        sector_writes = list(enumerate(sectors[-256:], 0x5D25))
        assert any(memory.scratch_writes[i:i + 256] == sector_writes
                   for i, (address, _) in enumerate(memory.scratch_writes) if address == 0x5D25)
        memory.scratch_writes = None
        cpu.set_tracer(ports)
    run_to(cpu, RETURN_SENTINEL)

    extra_fixed = bytes(memory[INPUT + len(raw):0xC000])
    old_page14 = bytes((index * 17 + 53) & 255 for index in range(0x4000))
    memory.banks[14][:] = old_page14
    start_call(cpu, 0x492D)
    run_to(cpu, RETURN_SENTINEL)
    assert ports.pages == [0x5D, 0x5E] and registers[SP] == 0x5BFE
    first = 178 * ROW_BYTES
    assert bytes(memory.banks[13][:first]) == raw[:first]
    assert not any(memory.banks[13][first:])
    second_start = 0x54
    second = raw[first:] + extra_fixed + old_page14[:80]
    wanted = bytearray(old_page14)
    wanted[second_start:second_start + len(second)] = second
    assert memory.banks[14] == wanted
    assert len(raw[first:]) == 25 * ROW_BYTES and len(second) == 26 * ROW_BYTES
    assert int.from_bytes(memory[0x4A44:0x4A46], 'little') == ROW_BYTES - 32
    assert int.from_bytes(memory[0x4A57:0x4A59], 'little') == INPUT + (90 - 32) // 2
    background = check_background(cpu, ports, raw) if check_full_background else None

    # Сверка окон, включая обе физические страницы и первую и последнюю строки.
    window_bytes = 0
    for row, count, column in ((0, 8, 29), (170, 8, 60), (178, 8, 0), (195, 8, 29)):
        page = 13 if row < 178 else 14
        source = 0xC000 + (row * ROW_BYTES if page == 13 else second_start + (row - 178) * ROW_BYTES) + column
        memory.out7ffd(0x50 + page - 8)
        screen = bytearray(memory[0x4000:0x5B00])
        # Окно не пересекает код, который исполняется по 4A00.
        dest = bitmap_address(95)
        for index in range(count):
            destination = bitmap_address(95 - index) - 0x4000
            begin = (row + index) * ROW_BYTES + column
            screen[destination:destination + 32] = raw[begin:begin + 32]
        start_call(cpu, 0x4A00, AF=count << 8, HL=source, DE=dest)
        run_to(cpu, RETURN_SENTINEL)
        assert bytes(memory[0x4000:0x5B00]) == screen, (row, count, column)
        window_bytes += count * 32

    return dict(file_key=key.decode('ascii'), sector_tail_supplied=include_sector_tail,
                loaded_bytes=len(data), initial_destination=INPUT, width_bytes=ROW_BYTES, height=HEIGHT,
                first_page=13, first_page_rows=178, second_page=14, second_page_start=second_start,
                second_page_rows=25, extra_fixed_bytes=len(extra_fixed), extra_bank_bytes=80,
                window_bytes_compared=window_bytes, trdos_substituted=rom_profile is None,
                physical_file_reads=file_reads, full_background=background)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dos-rom', type=Path)
    args = parser.parse_args()
    cases = [exercise(False, check_full_background=args.dos_rom is None), exercise(True)]
    rom_hash = None
    if args.dos_rom:
        basic, dos, sysvars = model_rom_context(args.dos_rom)
        cases.append(exercise(False, (basic, dos, sysvars), check_full_background=True))
        rom_hash = hashlib.sha256(dos).hexdigest()
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(), total_cases=len(cases),
                  archived_loader_disk_offset=FIXED_OFFSET, profiles=cases, dos_rom_sha256=rom_hash,
                  real_trdos_profile_executed=rom_hash is not None,
                  machine_paging_model=True, active_game_entry_proved=False,
                  native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/Scene1ArchiveConsumerVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{len(cases)} профиля scene1po, 203 строки в двух страницах, по 1024 байта вывода')


if __name__ == '__main__':
    main()
