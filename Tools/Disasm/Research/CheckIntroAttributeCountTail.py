"""Условное исполнение исходного хвоста 7497 после фактического переноса вступления."""

import json
import re

from CheckIntro import ROOT, PC, SP, Simulator, execute, original_memory, word
from skoolkit.simutils import get_registers


ENTRY, STOP = 0x7497, 0x74CD
ATTRIBUTES, SAMPLE = 0x5800, 0x8157
RETURN, INITIAL_SP = 0x3FFF, 0xBFFE


class Ports:
    def __init__(self):
        self.writes = []

    def write_port(self, registers, port, value, offset):
        self.writes.append((port, value))


class SampleMemory(list):
    def __init__(self, image):
        super().__init__(image)
        self.samples = []

    def __setitem__(self, address, value):
        if address == SAMPLE:
            self.samples.append(value)
        super().__setitem__(address, value)


def subtraction_flags(left, right, result):
    return (((result >> 8) & 0xA8) | (0x40 if result == 0 else 0) |
            (0x10 if (left & 0xFFF) < (right & 0xFFF) else 0) |
            (0x04 if ((left ^ right) & (left ^ result) & 0x8000) else 0) |
            0x02 | (left < right))


def check(image, count_base, scan, seed):
    memory = SampleMemory(image)
    memory[ATTRIBUTES:ATTRIBUTES + 256] = [(i * 53 + seed * 29) & 255 for i in range(256)]
    for address in set(range(count_base, count_base + 8)) | set(range(scan, scan + 7)):
        memory[address] = ((address * 19 + seed * 37) ^ (seed * 11)) & 255
    expected = memory.copy()
    expected[count_base] = count_base & 255
    for offset in range(7):
        expected[scan + offset] = expected[count_base + offset]
    expected[SAMPLE] = (expected[ATTRIBUTES + 254] >> 3) & 7
    expected[count_base] = (expected[count_base] + 255) & 255
    winner = max((count_base, *range(scan, scan + 7)), key=expected.__getitem__)
    result = (winner - count_base) & 65535
    flags = subtraction_flags(winner, count_base, result)
    for index, value in enumerate((count_base, scan, count_base, count_base), 1):
        word(expected, INITIAL_SP - 2 * index, value)

    sim = Simulator(memory)
    ports = Ports()
    sim.set_tracer(ports)
    initial = get_registers({'PC': ENTRY, 'SP': INITIAL_SP, 'HL': count_base, 'DE': scan,
                             'AF': 0xE5D7, 'BC': 0xCA35, 'IY': 0x5C3A,
                             '^HL': 0x1357, '^DE': 0x2468, '^BC': 0x369C, '^AF': 0x55AA}, None, False)
    sim.registers[:] = initial
    for _ in range(5000):
        if sim.registers[PC] == RETURN:
            break
        sim.run()
    else:
        raise AssertionError('условный вход 7497 не вернулся')
    registers = sim.registers
    assert memory == expected, (count_base, scan, seed, 'RAM')
    assert registers[:10] == [result & 255, flags, 0, 0, count_base >> 8, count_base & 255,
                               result >> 8, result & 255, count_base >> 8, count_base & 255]
    assert registers[10:12] == initial[10:12] and registers[16:24] == initial[16:24]
    assert registers[SP] == INITIAL_SP + 2
    assert memory.samples == [(value >> 3) & 7 for value in expected[ATTRIBUTES:ATTRIBUTES + 255]]
    assert ports.writes == [(((result & 255) << 8) | 0xFE, result & 255)]


def main():
    image = original_memory()
    expected = bytes(image[0x8F97:0x8FCD])
    assert expected == bytes.fromhex(
        'E5 D5 E5 E5 01 07 00 75 ED B0 06 FF 21 00 58 DD E1 7E 1F 1F 1F E6 07 32 57 81 '
        'DD 34 00 23 10 F1 D1 E1 06 07 1A BE 30 02 5D 54 23 10 F7 E1 B7 EB ED 52 7D D3 FE C9')
    execute(image, {'PC': 0x651D}, stop=0x6528)
    assert bytes(image[ENTRY:STOP]) == expected
    regions = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    branch = re.compile(r'^(?:CALL|JR|JP|DJNZ) (?:[A-Z]+,\s*)?#([0-9A-F]{4})$')
    for region in regions:
        if region['name'] not in ('Intro', 'IntroUnpack'):
            continue
        for row in region['instructions']:
            if region['name'] == 'IntroUnpack' and ENTRY <= row['address'] < STOP:
                continue
            match = branch.fullmatch(row['operation'])
            assert not match or not ENTRY <= int(match[1], 16) < STOP
    cases = 0
    for low in (0, 1, 7, 31, 63, 127, 247, 248):
        base = 0x9000 + low
        for scan in (base - 1, base, base + 1, 0x9200):
            for seed in range(32):
                check(image, base, scan, seed)
                cases += 1
    report = dict(passed=True, total_cases=cases, entry=ENTRY, physical_offset=0x2C97,
                  bytes=STOP - ENTRY, input_attributes=255, sample_destination=SAMPLE,
                  actual_index_displacement=0, direct_game_entry_found=False,
                  original_relocation_executed=True, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/IntroAttributeCountTailVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
