"""Условный вход E867 и арифметический результат исходного E869 для каждого HL.

Документация: ../../../Docs/PreviewSquareEntry.md#полный-r-условного-квадрата
"""

import json
import re

from Analyze import payload
from CheckIntro import ROOT
from CheckPreviewCoordinateMultiply import Memory
from PreviewFaceProductOracle import product
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, R, SP, get_registers
from PackedRefreshTrace import PackedRefreshTrace


def main():
    raw = payload(6)
    assert raw[0x2867:0x2869] == bytes.fromhex('54 5D')
    memory = Memory([0] * 65536)
    memory[0xC000:0xC000 + len(raw)] = raw
    memory[0x7FFE:0x8000] = [255, 63]
    simulator = Simulator(memory)
    regions = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    flow = next(region for region in regions if region['name'] == 'D3D')
    target = re.compile(r'^(?:CALL|JP|JR|DJNZ) (?:[A-Z]+,\s*)?#E86[78]$')
    assert not any(target.fullmatch(row['operation']) for row in flow['instructions'])
    code=[row for row in flow['instructions'] if 0xE867<=row['address']<0xEA01]
    for row in code:
        instruction=bytes.fromhex(row['hex']);address=row['address']
        assert raw[address-0xC000:address-0xC000+len(instruction)]==instruction
    refresh=PackedRefreshTrace(code,0);m1_bounds=[99999,0];total_m1=0
    for value in range(65536):
        initial = get_registers({'SP': 0x7FFE, 'PC': 0xE867, 'R': value & 255, 'HL': value,
                                 'DE': value ^ 0xFFFF, 'BC': 0x36C9, 'AF': 0x5A5D,
                                 'IX': 0x2468, 'IY': 0x5C3A, '^HL': 0x369C,
                                 '^DE': 0x47AD, '^BC': 0x58BE, '^AF': 0x69CF}, None, False)
        initial[14], initial[26], initial[27] = value & 255, value&1, value % 3
        simulator.registers[:] = initial
        memory.recording, memory.writes = True, []
        refresh.initial_r=initial[R];refresh.m1=refresh.steps=0;refresh.prefix_counts.clear()
        for _ in range(2):
            refresh.before(memory,simulator.registers[PC],simulator.registers[R])
            simulator.run();refresh.after(simulator.registers[R])
        registers = simulator.registers
        assert registers[PC] == 0xE869 and registers[4:6] == initial[6:8]
        assert registers[:4] == initial[:4] and registers[6:13] == initial[6:13]
        assert registers[16:24] == initial[16:24] and not memory.writes
        assert registers[R] == ((initial[R] & 128) | ((initial[R] + 2) & 127))
        for _ in range(1024):
            if registers[PC]==0x3FFF:break
            refresh.before(memory,registers[PC],registers[R]);simulator.run();refresh.after(registers[R])
        else:raise AssertionError(('square instruction limit',value))
        refresh.finish(registers[R]);total_m1+=refresh.m1
        m1_bounds[0]=min(m1_bounds[0],refresh.m1);m1_bounds[1]=max(m1_bounds[1],refresh.m1)
        expected = product(value, value)
        # Проверка математического квадрата непосредственно, край 8000 сохраняет исходную эффективную величину 256.
        signed_value = value - 65536 if value & 32768 else value
        square = 0x00800000 if value == 0x8000 else signed_value * signed_value
        assert (registers[6] << 24 | registers[7] << 16 | registers[4] << 8 | registers[5]) == square
        assert registers[:2] == [0, 0x44]
        assert all(registers[i] == initial[i] for i in (14, 26, 27))
        assert registers[:2] == list(expected['af'])
        for index, name in ((2, 'bc'), (4, 'de'), (6, 'hl'), (8, 'ix')):
            assert (registers[index] << 8 | registers[index + 1]) == expected[name]
        assert registers[10:12] == initial[10:12] and registers[16:24] == initial[16:24]
        assert registers[SP] == 0x8000
        assert len(memory.writes) == 2 and set(memory.writes) == {(0x7FFC, 0x44), (0x7FFD, 0)}
    report = dict(passed=True, cases=65536, entry=0xE867, continuation=0xE869,
                  special_8000_result=product(0x8000, 0x8000)['result'],
                  direct_bank_4_caller_found=False, game_entry_proved=False,
                  exact_integer_square_except_8000_checked=True, I_IM_IFF_preserved_checked=True,
                  entry_prefix_R_plus_2_checked=True, full_multiplier_R_proved=True,
                  full_M1_bounds=m1_bounds,total_M1=total_m1,each_R_step_and_bit7_checked=True,
                  independent_whole_multiply_M1_oracle=False,
                  complete_initial_context_product_exhausted=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/PreviewSquareEntryVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
