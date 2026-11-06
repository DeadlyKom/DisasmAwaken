"""Обход исходных строк 7799 с реальным поиском и пометкой записей."""
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from skoolkit.simutils import IXh, IXl


def word(memory, address):
    return memory[address] + 256 * memory[address + 1]


def signed(value):
    return value if value < 32768 else value - 65536


def main():
    memory = flat_action()
    memory[0xBFFE:0xC000] = [255, 63]
    sim = Simulator(memory)
    initial = [((offset * 43 + 7) & 255) for offset in range(64)]
    initial[:2] = [0, 128]
    initial[24] = 0
    cases = 0
    for index, capacity, overflow in product(range(16), (0, 1, 3, 16), (None, 0, 1, 2)):
        row = word(memory, 0x7799 + index * 2)
        before = memory[row:row + 8]
        if overflow is not None:
            memory[row + overflow * 2:row + overflow * 2 + 2] = [1, 0]
        for slot in range(capacity):
            address = 0xA100 + slot * 64
            memory[address:address + 64] = initial
        marker = 0xA100 + capacity * 64
        memory[marker:marker + 2] = [128, 128]
        memory[0x792E] = 16
        groups = [[0x1234, 0x5678, 0x5A5A], [32767, 32767, 32767]]
        expected = [initial.copy() for _ in range(capacity)]
        ptr = row
        for record in expected:
            groups[0][1] = 64
            groups.reverse()
            sums = [signed(value) + signed(word(memory, ptr + axis * 2))
                    for axis, value in enumerate(groups[0])]
            record[:4] = list((sums[0] & 65535).to_bytes(2, 'little')
                              + (sums[1] & 65535).to_bytes(2, 'little'))
            if any(not -32768 <= value <= 32767 for value in sums):
                record[:2] = [0, 128]
                record[24] = 255
                break
            record[4:6] = list((sums[2] & 65535).to_bytes(2, 'little'))
            record[6:14] = [memory[ptr + 6], 0, memory[ptr + 7], 0, 9, 0, 0, 0]
            record[15:25] = [0, 0, 0, 0x12, 255, 255, 255, 0, 0, memory[0x792E] if ptr == row else 0]
            record[36] = 0
            ptr += 8
            if memory[ptr + 1] == 128:
                break
        sim.registers[:] = get_registers({'PC': 0x78A1, 'SP': 0xBFFE, 'IX': row,
                                          'HL': 0x1234, 'DE': 0x5678, 'BC': 0x5A5A,
                                          '^HL': 32767, '^DE': 32767, '^BC': 32767}, None, False)
        for _ in range(7000):
            if sim.registers[PC] == 0x3FFF:
                break
            sim.run()
        context = (index, capacity, overflow)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert sim.registers[IXh] * 256 + sim.registers[IXl] == ptr, context
        for slot, record in enumerate(expected):
            address = 0xA100 + slot * 64
            actual = memory[address:address + 64]
            assert actual == record, (context, slot, [(n, a, b) for n, (a, b) in enumerate(zip(actual, record)) if a != b])
        assert memory[0x792E] == (16 if ptr == row else 0), context
        memory[row:row + 8] = before
        cases += 1
    report = dict(passed=True, total_cases=cases, all_original_template_pointers=True,
                  injected_overflow_per_axis=True, whole_records_compared=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnTemplateLoopVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
