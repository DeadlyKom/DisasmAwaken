"""Проверка общих адресов LANG и физических записей STATIONF на исходных байтах."""
import json

from CheckActiveNeighbors import ROOT, Simulator, get_registers, reference
from CheckMarketAccess import add16_flags
from skoolkit.simutils import A, B, C, D, E, F, H, L, SP


def main():
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    sources = {
        entry['slot']: (ROOT / (entry['path'] + '.sectors.bin')).read_bytes()
        for entry in manifest['entries'] if entry['slot'] in (4, 5)
    }
    memory = bytearray(65536)
    memory[0x6000:0xC000] = sources[4][:0x6000]
    memory[0xC000:0xC000 + len(sources[5])] = sources[5]
    simulator = Simulator(memory)
    initial = get_registers({'SP': 0x7FFA, 'AF': 0x5AC5, 'BC': 0x36C9}, None, False)
    counts = {}

    def execute(entry, index):
        memory[0x7FFA:0x7FFE] = bytes((index, index ^ 255, 255, 63))
        simulator.registers[:] = initial
        simulator.run(start=entry, stop=0x3FFF)
        registers = simulator.registers
        assert registers[SP] == 0x7FFE
        return registers

    for entry, base, width, physical_count in (
        (0xC4D7, 0x9592, 2, 33), (0xC58A, 0x95D4, 2, 14),
        (0xC4E3, 0x95F1, 1, 33), (0xC590, 0x9633, 1, 14),
    ):
        for index in range(256):
            address = base + 2 * index
            expected = int.from_bytes(memory[address:address + width], 'little')
            r = execute(entry, index)
            assert r[D] * 256 + r[E] == expected
            assert r[H] * 256 + r[L] == address + width - 1
            assert (r[A], r[F]) == (0x5A, add16_flags(2 * index, base, 0xC5))
        counts[f'{entry:04X}'] = dict(cases=256, physical_records=physical_count)

    for entry, bounds, values, physical_count in (
        (0xC51A, 0x964E, 0x988E, 33), (0xC5A9, 0x9690, 0x98F6, 13),
    ):
        for index in range(256):
            expected = reference(memory, index, bounds, values)
            r = execute(entry, index)
            assert (r[A], r[F], r[H] * 256 + r[L], r[C], r[D] * 256 + r[E]) == expected
            assert r[B] == bounds >> 8
        for index in range(physical_count):
            left, right = memory[bounds + 2 * index:bounds + 2 * index + 2]
            first = index - ((-left) & 255)
            last = index + right
            assert 0 <= first <= index <= last < physical_count
            assert all(memory[bounds + 2 * neighbor:bounds + 2 * neighbor + 2]
                       == bytes(((first - neighbor) & 255, last - neighbor))
                       for neighbor in range(first, last + 1))
        counts[f'{entry:04X}'] = dict(cases=256, physical_records=physical_count)

    assert memory[0x9690 + 2 * 13:0x9690 + 2 * 14] == bytes(2)
    assert memory[0x9592:0x96AC] == sources[4][0x3592:0x36AC]
    report = dict(passed=True, cases=sum(item['cases'] for item in counts.values()), entries=counts,
                  original_station_tables=True, second_index_13_reads_keyboard_anchor=True,
                  contiguous_neighbor_groups=True, out_of_range_gameplay_proved=False,
                  assembly_executed=False, native_execution=False)
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/EquipmentPhysicalTablesVerification.json').write_text(output, 'utf-8')
    print(output, end='')


if __name__ == '__main__':
    main()
