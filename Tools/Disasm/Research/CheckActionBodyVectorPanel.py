"""Оценка рабочего вектора 67F5 и подготовка запросов панели."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(flat_action())
    memory[0xBFFE:0xC000] = [255, 63]
    sim = Simulator(memory)
    outcomes = Counter()

    def check(values, old, guard, phase, mode, bias, stock, cap, preferred, fallback):
        for address, value in zip((0x9B6F, 0x9B72, 0x9B75), values):
            memory[address:address + 3] = list(value.to_bytes(3, 'little'))
        for address, value in ((0x6682, old), (0x9C29, guard), (0x683C, phase), (0x9B81, mode),
                               (0x6874, bias), (0x9BD2, stock), (0x9BD3, cap),
                               (0x9C10, preferred), (0x9C11, fallback)):
            memory[address] = value
        maximum = max(min(value >> 16, 255 - (value >> 16)) for value in values)
        writes = [(0xBFFC, 0xF8), (0xBFFD, 0x67)]
        destination = 0x688A
        if maximum:
            if old:
                writes.extend(((0x667D, old), (0x6682, 0)))
            if maximum >= 28:
                writes.append((0x7B6B, min(255, maximum - 27 + bias)))
            if maximum >= 64 and mode != 2:
                destination = 0x6727
            outcome = 'far'
        else:
            middle = [((-1 if value & 0x800000 else 1) * (value >> 8)) & 255 for value in values]
            gauge = min(46, ((-max(middle)) & 255) // 2)
            writes.extend(((0x6682, gauge), (0x667D, 1)))
            if guard == 255:
                destination = 0x3FFF
                outcome = 'guard_return'
            else:
                writes.append((0x683C, (phase >> 1) | ((phase & 1) << 7)))
                outcome = 'phase_wait'
                if phase & 1:
                    writes.extend(((0xBFFC, 0x47), (0xBFFD, 0x68)))
                    candidate = (stock + 1) & 255
                    outcome = 'stock_at_limit'
                    if candidate <= cap:
                        address, value = (0x9C10, preferred) if preferred else (0x9C11, fallback)
                        writes.extend(((0x9BD2, candidate), (0x9BD3, cap), (address, (value + 1) & 255)))
                        outcome = 'stock_incremented'
                    writes.append((0x665C, 1))
        sim.registers[:] = get_registers({'PC': 0x67F5, 'SP': 0xBFFE}, None, False)
        memory.writes = []
        memory.recording = True
        for _ in range(120):
            if sim.registers[PC] in (0x6727, 0x688A, 0x3FFF):
                break
            sim.run()
        memory.recording = False
        context = (values, old, guard, phase, mode, bias, stock, cap, preferred, fallback, outcome)
        assert sim.registers[PC] == destination, context
        assert sim.registers[SP] == (0xC000 if destination == 0x3FFF else 0xBFFE), context
        assert Counter(memory.writes) == Counter(writes), (context, memory.writes, writes)
        outcomes[outcome] += 1

    for high, old, mode, bias in product(range(256), (0, 1, 255), (0, 2), (0, 1, 255)):
        check((high << 16, 0, 0), old, 255, 0, mode, bias, 0, 0, 0, 0)
    for middle, phase, guard in product(range(256), (0, 1, 2, 255), (0, 255)):
        check((middle << 8, 0xFF0000 | (middle << 8), 0), 0, guard, phase, 0, 0, middle, 127, 0, 255)
    for stock, cap in product(range(256), repeat=2):
        check((0, 0, 0), 0, 0, 1, 0, 0, stock, cap, stock & 1, 255)
    assert len(outcomes) == 5
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes),
                  all_stock_limit_pairs=True, write_multiplicity_checked=True,
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionBodyVectorPanelVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
