"""R, стек и сохраняемые регистры F931/F957 без исполнения сборки.

Документация: ../../../Docs/VoxelSmallArithmetic.md
"""
from hashlib import sha256
from itertools import product
import json

from CheckEffects import memory_image
from CheckMusicGateTicks import Memory
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from ReferenceControlsPointRespawn import refresh
from ReferenceVoxelSmallArithmetic import divide_value_m1, multiply_m1
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def execute(cpu, entry, initial, expected_m1):
    cpu.registers[:] = initial
    memory = cpu.memory
    memory.writes = []
    memory.recording = True
    actual_m1 = 0
    for _ in range(160):
        pc = cpu.registers[PC]
        if pc == 0x3FFF:
            break
        assert entry <= pc < (0xF957 if entry == 0xF931 else 0xF9E9)
        opcode = memory[pc]
        assert opcode not in (0xDD, 0xED, 0xFD)
        actual_m1 += 2 if opcode == 0xCB else 1
        cpu.run()
        assert cpu.registers[R] == refresh(initial[R], actual_m1)
    else:
        raise AssertionError(('arithmetic_instruction_limit', entry))
    memory.recording = False
    assert not memory.writes and cpu.registers[SP] == 0xC000
    assert actual_m1 == expected_m1, (entry, initial[:8], actual_m1, expected_m1)


def initial_registers(entry, case, **values):
    registers = dict(PC=entry, SP=0xBFFE, HL=0x1357, DE=0x2468, BC=0x369C,
        AF=0x5A96, IX=0x47AD, IY=0x58BE, I=0x3C, R=case & 255,
        **{'^HL':0x69CF, '^DE':0x7AD0, '^BC':0x8BE1, '^AF':0x9CF2})
    registers.update(values)
    return get_registers(registers, {'im':2, 'iff':0}, False)


def main():
    baseline = memory_image()
    code = bytes(baseline[0xF931:0xF9E9])
    offset = ENTRIES[21]['offset'] + 0xD31
    assert code == DISK[offset:offset + len(code)]
    memory = Memory(baseline)
    cpu = Simulator(memory)
    multiply_costs, divide_costs, sampled_r = set(), set(), set()
    common_preserved = (*range(8, 12), 14, *range(16, 24), 26, 27)
    multiply_cases = 0
    for case, (a, word, carry) in enumerate(product(range(256),
            (0, 1, 255, 256, 0x7FFF, 0x8000, 0xFFFF), (0, 1))):
        initial = initial_registers(0xF931, case, BC=word, AF=a * 256 + carry)
        cost = multiply_m1(a)
        execute(cpu, 0xF931, initial, cost)
        r = cpu.registers
        assert r[6] * 256 + r[7] == ((a & 127) * word) & 65535
        assert all(r[i] == initial[i] for i in (*range(2, 6), *common_preserved))
        multiply_costs.add(cost)
        sampled_r.add(initial[R])
        multiply_cases += 1
    divide_cases = 0
    for case, (a, divisor) in enumerate(product(range(256), range(1, 256))):
        initial = initial_registers(0xF957, case, DE=0x2400 | divisor, AF=a * 256 + (case & 1))
        expected, cost = divide_value_m1(a, divisor)
        execute(cpu, 0xF957, initial, cost)
        r = cpu.registers
        assert r[4] * 256 + r[5] == expected, (a, divisor, expected, r[:8])
        assert r[0] == r[4] and r[3] == (r[4] ^ 255) and r[7] == (r[5] ^ 255)
        assert all(r[i] == initial[i] for i in (2, 6, *common_preserved))
        if divisor <= 128:
            assert expected == ((a & 127) * 256) // divisor
        divide_costs.add(cost)
        sampled_r.add(initial[R])
        divide_cases += 1
    assert sampled_r == set(range(256))
    report = dict(passed=True, multiply_cases=multiply_cases, divide_cases=divide_cases,
                  original_arithmetic_code_sha256=sha256(code).hexdigest(),
                  independent_numeric_results_and_M1_formulas=True, r_checked_after_every_instruction=True,
                  observed_multiply_M1=sorted(multiply_costs), observed_divide_M1=sorted(divide_costs),
                  all_nonzero_byte_divisors_checked=True, ordinary_division_proved_only_for_divisors_1_to_128=True,
                  preserving_H_B_for_divide_checked=True, preserving_BC_DE_for_multiply_checked=True,
                  alternative_and_index_registers_I_IM_IFF_preserved=True,
                  no_memory_writes=True, final_SP=0xC000,
                  initial_r_codes_sampled_across_cases=sorted(sampled_r),
                  all_initial_r_codes_crossed_with_all_inputs=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/VoxelSmallArithmeticRefreshVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены результаты, M1, R и сохранение регистров двух семибитовых помощников VOXAL.')


if __name__ == '__main__':
    main()
