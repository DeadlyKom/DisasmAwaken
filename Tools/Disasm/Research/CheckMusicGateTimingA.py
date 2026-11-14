"""Входы длительностей A/C, оригинальные байты, записи и полный R.

Документация: ../../../Docs/MusicEffects.md#длительности-a-и-регистр-r
"""
from pathlib import Path
import json

from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from PackedRefreshTrace import PackedRefreshTrace

ROOT = Path(__file__).resolve().parents[3]


def main(channel='A'):
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    memory = Memory([0] * 65536)
    memory[0xDB00:0xDB00 + len(raw)] = raw
    # Проверка обеих исходных последовательностей, JR ведёт в общий хвост.
    code = ((0xDDCA, '1a'), (0xDDCB, '13'), (0xDDCC, '1804'),
            (0xDDD2, '3297de'), (0xDDD5, '1a'), (0xDDD6, '13'),
            (0xDDD7, '329fde'), (0xDDDA, '3e06'),
            (0xDDDC, '3290de'), (0xDDDF, 'c9'))
    read_entry, set_entry = 0xDDCA, 0xDDD2
    targets = (0xDE97, 0xDE9F, 0xDE90)
    costs = (10, 7)
    if channel == 'C':
        read_entry, set_entry = 0xDE0A, 0xDE12
        code = ((0xDE0A, '1a'), (0xDE0B, '13'), (0xDE0C, '1804'),
                (0xDE12, '32e7e2'), (0xDE15, '32d5e2'),
                (0xDE18, '1a'), (0xDE19, '13'),
                (0xDE1A, '32e3e2'), (0xDE1D, 'c9'))
        targets = (0xE2E7, 0xE2D5, 0xE2E3)
        costs = (9, 6)
    else:
        assert channel == 'A'
    for address, encoded in code:
        assert bytes(memory[address:address + len(bytes.fromhex(encoded))]).hex() == encoded
    simulator = Simulator(memory)
    counts = {}
    for entry, cost in zip((read_entry, set_entry), costs):
        trace = PackedRefreshTrace([dict(address=a, hex=h) for a, h in code], 0)
        seeds = set()
        total = 0
        # Проверка всех пар длительностей, нуль не нормализуется.
        for first in range(256):
            for second in range(256):
                memory.recording = False
                memory[0x7000:0x7002] = [first, second]
                memory[0x7FFE:0x8000] = [0xFF, 0x3F]
                for target in targets:
                    memory[target] = 0xA5
                initial = get_registers({
                    'HL': 0x1357, 'DE': 0x7000 if entry == read_entry else 0x7001,
                    'BC': 0x2468, 'AF': first * 256 + second,
                    'IX': 0xABCD, 'IY': 0x5C3A, '^HL': 0x1234,
                    '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0,
                    'SP': 0x7FFE, 'PC': entry, 'R': first, 'I': second,
                }, None, False)
                initial[26] = second & 1
                initial[27] = second % 3
                simulator.registers[:] = initial
                registers = simulator.registers
                trace.initial_r = registers[15]
                trace.m1 = trace.steps = 0
                trace.prefix_counts.clear()
                seeds.add(registers[15])
                memory.writes = []
                memory.recording = True
                # Проверка каждой команды, включая JR и настоящий RET.
                for _ in range(cost):
                    trace.before(memory, registers[PC], registers[15])
                    simulator.run()
                    trace.after(registers[15])
                trace.finish(registers[15])
                memory.recording = False
                assert trace.m1 == trace.steps == cost
                assert registers[PC] == 0x3FFF and registers[SP] == 0x8000
                assert registers[0] == (6 if channel == 'A' else second)
                assert registers[1] == second
                assert registers[4] * 256 + registers[5] == 0x7002
                assert all(registers[i] == initial[i] for i in
                           (2, 3, 6, 7, 8, 9, 10, 11, 14, *range(16, 24), 26, 27))
                expected_writes = ([(0xDE97, first), (0xDE9F, second), (0xDE90, 6)]
                                   if channel == 'A' else
                                   [(0xE2E7, first), (0xE2D5, first), (0xE2E3, second)])
                assert memory.writes == expected_writes
                total += trace.m1
        assert len(seeds) == 256
        counts[f'{entry:04X}'] = dict(cases=65536, m1_per_call=cost, total_m1=total)
    report = dict(passed=True, channel=channel, entries=counts, total_cases=131072,
                  all_duration_pairs=True, all_initial_R_values_per_entry=True,
                  all_input_flags_per_entry=True, full_joint_register_cartesian=False,
                  every_instruction_and_R_step_checked=True,
                  every_cpu_write_checked=True, I_IM_IFF_preserved=True,
                  fixed_disjoint_stream_and_stack_fixture=True,
                  all_address_aliases_proved=False, irq_executed=False,
                  full_music_playback_proved=False, assembly_executed=False)
    (ROOT / f'Tools/Disasm/Reports/MusicGateTiming{channel}Verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
