"""Все 16-битные состояния изменяемого операнда по 6781."""
from collections import Counter
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    paths = Counter()
    targets = (0x688A, 0x6742, 0x6765, 0x679B)
    for value in range(65536):
        for mode in (0, 1, 2, 255):
            memory[0x6781:0x6783] = list(value.to_bytes(2, 'little'))
            memory[0x9B81] = mode
            sim.registers[:] = get_registers({'PC': 0x6780, 'SP': 0xBFFE}, None, False)
            writes = [(0x6781, (value >> 1) & 255), (0x6782, value >> 9)]
            target = 0x688A
            if value & 1:
                writes.extend(((0x6781, (value >> 1) & 255), (0x6782, 128 | value >> 10)))
                target = {1: 0x6742, 2: 0x6765}.get(mode, 0x679B)
            memory.recording = True
            memory.writes = []
            for _ in range(20):
                if sim.registers[PC] in targets:
                    break
                sim.run()
            memory.recording = False
            assert sim.registers[PC] == target and sim.registers[SP] == 0xBFFE, (value, mode)
            assert memory.writes == writes, (value, mode, memory.writes, writes)
            paths[f'{target:04X}'] += 1
    report = dict(passed=True, total_cases=paths.total(), paths=dict(paths),
                  all_operand_words=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionBodyVectorScheduleVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
