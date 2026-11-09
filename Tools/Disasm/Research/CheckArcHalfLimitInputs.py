"""Независимая проверка E289, разность полуширины и смещения по модулю 256."""
import json

from CheckArcPreparation import ROOT, Simulator, get_registers, make_context
from skoolkit.simutils import A, B, C, F, PC, R, SP, T


def main():
    _, source, _ = make_context()
    memory = bytearray(65536)
    memory[0xC000:0xC000 + len(source)] = source
    assert memory[0xE289:0xE299] == bytes.fromhex('ed4bafdf3ac1df90d94f3ab3df5fd9c9')
    memory[0x7FFE:0x8000] = bytes((255, 63))
    sim = Simulator(memory)
    initial = get_registers({'PC': 0xE289, 'SP': 0x7FFE, 'HL': 0x1357, 'DE': 0x247A,
                             'BC': 0x36C9, 'AF': 0x5A5D, 'IX': 0x2468, 'IY': 0x5C3A,
                             '^HL': 0x369C, '^DE': 0x47AD, '^BC': 0x58BE, '^AF': 0x69CF}, None, False)
    expected_memory = memory.copy()
    for half in range(256):
        for offset in range(256):
            vertical, start = (half + 19 * offset) & 255, (31 * half + offset) & 255
            for address, value in ((0xDFAF, vertical), (0xDFB0, offset), (0xDFB3, start), (0xDFC1, half)):
                memory[address] = expected_memory[address] = value
            result = (half - offset) & 255
            flags = (result & 0xA8) | 2 | int(half < offset)
            flags |= 0x40 if result == 0 else 0
            flags |= 0x10 if (half & 15) < (offset & 15) else 0
            flags |= 4 if (half ^ offset) & (half ^ result) & 0x80 else 0
            initial[R] = offset
            expected = initial.copy()
            expected[A], expected[F], expected[B], expected[C] = start, flags, offset, vertical
            expected[19], expected[21] = result, start
            expected[PC], expected[SP], expected[T] = 0x3FFF, 0x8000, 76
            expected[R] = (offset & 128) | ((offset + 10) & 127)
            sim.registers[:] = initial
            for _ in range(9):
                sim.run()
            assert sim.registers == expected, (half, offset, sim.registers, expected)
            assert memory == expected_memory
    proof = dict(passed=True, total_cases=65536, exact_flags_r_sp_and_memory=True,
                 instructions_executed=9, t_states=76, normal_game_caller_proved=False,
                 irq_executed=False, native_execution=False, assembly_executed=False)
    path = ROOT / 'Tools/Disasm/Reports/ArcHalfLimitInputsVerification.json'
    path.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
