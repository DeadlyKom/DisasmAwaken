"""Ветка 7C78 с поиском записи класса #12 и смещением её второй компоненты."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceControlsPointRespawn import refresh


def main():
    memory = flat_action()
    sim = Simulator(memory)
    outcomes = Counter()
    for seed, cls, enabled, found in product(range(256), range(9), (0, 1), (False, True)):
        memory[0x9B83] = enabled
        memory[0xA100:0xA106] = [0xEF, 0x7E, 0x90, 0xFF, 0x12, 0x34]
        memory[0xA112] = 18 if found else 19
        memory[0xA140:0xA142] = [128, 128]
        before = [(offset * 73 + seed) & 255 for offset in range(64)]
        before[18] = cls
        memory[0xA180:0xA1C0] = before
        selected = bool(refresh(seed, 2) & 2) and enabled and 1 <= cls <= 4 and found
        sim.registers[:] = get_registers({'PC': 0x7C78, 'SP': 0xBFFE, 'IX': 0xA180, 'DE': 0x1300}, None, False)
        sim.registers[15] = seed
        sample = None
        for _ in range(100):
            pc = sim.registers[PC]
            if pc in (0x7CDD, 0x7DD8):
                break
            if pc == 0x7CAF:
                sample = refresh(sim.registers[15], 2)
            sim.run()
        assert sim.registers[PC] == (0x7DD8 if selected else 0x7CDD) and sim.registers[SP] == 0xBFFE
        if selected:
            shift = 0x180 + (sample & 1) * 256
            before[:6] = [0xEF, 0x7E, *((0xFF90 + shift) & 65535).to_bytes(2, 'little'), 0x12, 0x34]
            before[7:11] = [64, 0, 0, 1]
            outcomes['copied'] += 1
        else:
            assert sample is None
            outcomes['fallback'] += 1
        assert memory[0xA180:0xA1C0] == before, (seed, cls, enabled, found, sample)
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  actual_record_search_executed=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnNearClass12Verification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
