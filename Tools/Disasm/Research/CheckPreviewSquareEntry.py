"""Условный вход E867 и арифметический результат исходного E869 для каждого HL."""

import json
import re

from Analyze import payload
from CheckIntro import ROOT
from CheckPreviewCoordinateMultiply import Memory
from PreviewFaceProductOracle import product
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, R, SP, get_registers


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
    for value in range(65536):
        initial = get_registers({'SP': 0x7FFE, 'PC': 0xE867, 'R': value & 255, 'HL': value,
                                 'DE': value ^ 0xFFFF, 'BC': 0x36C9, 'AF': 0x5A5D,
                                 'IX': 0x2468, 'IY': 0x5C3A, '^HL': 0x369C,
                                 '^DE': 0x47AD, '^BC': 0x58BE, '^AF': 0x69CF}, None, False)
        simulator.registers[:] = initial
        memory.recording, memory.writes = True, []
        simulator.run(stop=0xE869)
        registers = simulator.registers
        assert registers[PC] == 0xE869 and registers[4:6] == initial[6:8]
        assert registers[:4] == initial[:4] and registers[6:13] == initial[6:13]
        assert registers[16:24] == initial[16:24] and not memory.writes
        assert registers[R] == ((initial[R] & 128) | ((initial[R] + 2) & 127))
        simulator.run(stop=0x3FFF)
        expected = product(value, value)
        assert registers[:2] == list(expected['af'])
        for index, name in ((2, 'bc'), (4, 'de'), (6, 'hl'), (8, 'ix')):
            assert (registers[index] << 8 | registers[index + 1]) == expected[name]
        assert registers[10:12] == initial[10:12] and registers[16:24] == initial[16:24]
        assert registers[SP] == 0x8000
        assert len(memory.writes) == 2 and set(memory.writes) == {(0x7FFC, 0x44), (0x7FFD, 0)}
    report = dict(passed=True, cases=65536, entry=0xE867, continuation=0xE869,
                  special_8000_result=product(0x8000, 0x8000)['result'],
                  direct_bank_4_caller_found=False, game_entry_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/PreviewSquareEntryVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
