"""Три проекции слова A78F на коэффициенты третьей строки матрицы."""
from collections import Counter
import json

from CheckActionObjectOffsetVector import multiply
from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceControlsPointRespawn import refresh


def main():
    baseline = flat_action()
    memory = baseline.copy()
    memory[0xBFFE:0xC000] = [255, 63]
    sim = Simulator(memory)
    counts = Counter()

    def check(word, coefficients):
        for address, value in zip((0xCBD8, 0xCBEE, 0xCC09), coefficients):
            memory[address] = value
        memory[0xA78F:0xA791] = [word & 255, word >> 8]
        initial = get_registers({'PC': 0x6E72, 'SP': 0xBFFE, 'BC': 0x5A3C,
                                 '^AF': 0x1234, 'IX': 0xABCD, 'IY': 0x2468}, None, False)
        wanted = list(initial)
        cycles = 28
        products = []
        for coefficient in coefficients:
            value, fetches = multiply(wanted, coefficient, word)
            products.append(value)
            cycles += fetches
        wanted[8:10] = [0x6E, 0xA8]
        wanted[PC], wanted[SP], wanted[15] = 0x3FFF, 0xC000, refresh(initial[15], cycles)
        sim.registers[:] = initial
        sim.run(0x6E72, 0x3FFF)
        compared = (*range(13), 14, 15, *range(16, 25), 26, 27)
        assert all(sim.registers[i] == wanted[i] for i in compared), (
            word, coefficients, [(i, sim.registers[i], wanted[i]) for i in compared if sim.registers[i] != wanted[i]])
        for address, value in zip((0xE5B3, 0xE5D2, 0xE5ED), products):
            assert memory[address:address + 2] == [value & 255, value >> 8]
        counts['cases'] += 1

    for word in range(65536):
        check(word, (word & 255, word >> 8, (word * 73 + 17) & 255))
    report = dict(passed=True, total_cases=counts['cases'], every_input_word=True,
                  start=0x6E72, preceding_key_dispatch_executed=False, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionMotionVectorTailVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
