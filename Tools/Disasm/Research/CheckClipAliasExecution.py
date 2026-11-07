"""Условный вход CF08, точный эффект трёх байтов не доказывает игровой вызывающий путь."""
import json
from itertools import product

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import refresh


def main():
    memory = flat_action()
    mirror = (ROOT / 'Tools/Disasm/Extracted/Active/19_3DPART.C.bin').read_bytes()
    assert bytes(memory[0xCF08:0xCF0B]) == mirror[0xF08:0xF0B] == b'\xF3\xAF\xC9'
    memory[0xBFFE:0xC000] = [255, 63]
    before = list(memory)
    simulator = Simulator(memory)
    count = 0
    # Проверка всех флагов, обоих состояний IFF, трёх режимов IM и разных значений A.
    for a, flags, iff, mode in product((0, 1, 127, 128, 255), range(256), (0, 1), range(3)):
        initial = get_registers({'PC': 0xCF08, 'SP': 0xBFFE, 'AF': (a << 8) | flags,
                                 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                                 '^HL': 0xABCD, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEFF,
                                 'IX': 0xBEEF, 'IY': 0x5C3A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = count & 255, count & 255, iff, mode
        expected = list(initial)
        expected[0:2] = [0, 0x44]
        expected[PC], expected[SP], expected[26] = 0x3FFF, 0xC000, 0
        expected[15] = refresh(initial[15], 3)
        simulator.registers[:] = initial
        for _ in range(3):
            simulator.run()
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(simulator.registers[index] == expected[index] for index in compared)
        assert memory == before
        count += 1
    result = dict(passed=True, total_cases=count, original_alias_copies=2,
                  conditional_instruction_effect_proved=True, all_memory_unchanged=True,
                  exact_registers_flags_and_R=True, iff_cleared=True, instruction_count=3,
                  execution_entry_proved=False, nonexecution_proved=False,
                  unknown_purpose_preserved=True, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ClipAliasExecutionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
