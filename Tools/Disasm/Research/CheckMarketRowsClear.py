"""Очистка рынка A90D, все AF, точные флаги, записи и повторения LDIR.

Документация: ../../../Docs/RandomState.md#отдельный-хвост-очистки
"""
from pathlib import Path
import json

from CheckRandomState import RecordedMemory, make_context
from CheckMusic import Simulator, get_registers, PC, SP
from PackedRefreshTrace import PackedRefreshTrace

ROOT = Path(__file__).resolve().parents[3]


def main():
    _, _, banks = make_context()
    memory = RecordedMemory(65536)
    for start, page in ((0x4000, 5), (0x8000, 2), (0xC000, 0)):
        memory[start:start + 16384] = bytes(banks[page])
    # Проверка шести исходных команд, LDIR исполняется 59 раз.
    code = ((0xA90D, '215595'), (0xA910, '115695'), (0xA913, '013b00'),
            (0xA916, '3600'), (0xA918, 'edb0'), (0xA91A, 'c9'))
    trace = PackedRefreshTrace([dict(address=a, hex=h) for a, h in code], 0)
    simulator = Simulator(memory, config={'fast_ldir': False})
    for a in range(256):
        for f in range(256):
            memory.recording = False
            before = bytes((a + f + i * 71) & 255 for i in range(63))
            memory[0x9554:0x9593] = before
            memory[0x7FFE:0x8000] = bytes([255, 63])
            initial = get_registers({
                'AF': a * 256 + f, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                '^AF': 0x1234, '^HL': 0x5678, '^DE': 0x9ABC, '^BC': 0xDEF0,
                'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0x7FFE, 'PC': 0xA90D,
                'R': a, 'I': f,
            }, None, False)
            initial[26] = f & 1
            initial[27] = f % 3
            simulator.registers[:] = initial
            r = simulator.registers
            trace.initial_r = r[15]
            trace.m1 = trace.steps = 0
            trace.prefix_counts.clear()
            memory.writes = []
            memory.recording = True
            # Проверка каждого повторения LDIR и независимого полного счёта 4+59*2+1.
            for _ in range(64):
                trace.before(memory, r[PC], r[15])
                simulator.run()
                trace.after(r[15])
            trace.finish(r[15])
            memory.recording = False
            assert trace.m1 == 123 and r[PC] == 0x3FFF and r[SP] == 0x8000
            flags = (f & 0xC1) | (a & 8) | ((a & 2) << 4)
            assert r[:8] == [a, flags, 0, 0, 0x95, 0x91, 0x95, 0x90]
            assert all(r[i] == initial[i] for i in
                       (8, 9, 10, 11, 14, *range(16, 24), 26, 27))
            assert bytes(memory[0x9554:0x9593]) == before[:1] + bytes(60) + before[61:]
            assert memory.writes == [(address, 0) for address in range(0x9555, 0x9591)]
    report = dict(passed=True, cases=65536, all_AF_values=True,
                  all_initial_R_values=True, full_joint_register_cartesian=False,
                  full_m1_per_call=123, instructions_per_call=64,
                  LDIR_iterations_per_call=59, every_instruction_and_R_step_checked=True,
                  all_cpu_writes_checked=True, stack_bytes_written=0,
                  I_IM_IFF_preserved=True, fixed_disjoint_stack_fixture=True,
                  irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MarketRowsClearVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
