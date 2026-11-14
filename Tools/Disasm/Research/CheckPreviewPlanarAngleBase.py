"""Исходный префикс плоской модели для всех пар угла и базового отсчёта."""
import json

from CheckPreviewModelWalk import Memory, Simulator, ROOT, payload, get_registers
from skoolkit.simutils import A, B, F, H, L, PC, R, T


def main():
    raw = payload(6)
    memory = Memory([0] * 65536)
    memory[0xC000:0xC000 + len(raw)] = raw
    sine = bytes(memory[0xC400:0xC500])
    targets = (0xD861, 0xD87B, 0xD869, 0xD871)
    initial = get_registers(dict(PC=0xD819, SP=0x7FFE, AF=0xA55A,
                                HL=0x1357, DE=0x2468, BC=0x369C,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    cpu = Simulator(memory)
    stable = [i for i in range(len(initial)) if i not in (A, B, F, H, L, PC, R, T)]
    cases = 0
    for base in range(256):
        for angle in range(256):
            memory.recording = False
            memory[0xC201], memory[0xC21F] = base, angle
            for target in targets:
                memory[target] = 0xA5
            cpu.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(15):
                cpu.run()
            delta = (angle - base) & 255
            expected = [sine[(delta + 64) & 255]] * 2 + [sine[delta]] * 2
            assert cpu.registers[PC] == 0xD836
            assert [memory[p] for p in targets] == expected
            assert memory.writes == list(zip(targets, expected))
            assert (cpu.registers[A], cpu.registers[B], cpu.registers[H], cpu.registers[L]) == (sine[delta], delta, 0xC4, delta)
            assert all(cpu.registers[i] == initial[i] for i in stable)
            assert memory[0xC201] == base and memory[0xC21F] == angle
            cases += 1
    report = dict(passed=True, total_cases=cases, entry=0xD819, stop=0xD836,
                  base_address=0xC201, angle_address=0xC21F,
                  original_sine_used=True, exact_four_operand_writes=True,
                  complete_angle_pair_domain=True,
                  flags_r_t_checked=False, entire_model_executed=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/PreviewPlanarAngleBaseVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены все 65536 пар угла и базового отсчёта плоской модели.')


if __name__ == '__main__':
    main()
