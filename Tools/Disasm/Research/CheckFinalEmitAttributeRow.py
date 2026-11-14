"""Исходный генератор атрибутного фрагмента, весь домен операнда SP и все флаги штатных рядов."""
from collections import Counter
import json

from CheckFinal import ROOT, Simulator, get_registers, original_memory, word
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import A, B, C, D, E, F, H, IFF, L, PC, R, SP, T


def main():
    memory = Memory(original_memory())
    word(memory, 0x7FFC, 0xC35A)
    word(memory, 0x7FFE, 0x3FFF)
    cpu = Simulator(memory)
    initial = get_registers(dict(PC=0x6234, SP=0x7FFE, AF=0xA55A,
                                HL=0x1357, DE=0x9000, BC=0x369C,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    cases = 0

    def check(old, flags):
        nonlocal cases
        memory.recording = False
        word(memory, 0x6282, old)
        copied = memory[0x627D:0x6294]
        cpu.registers[:] = initial
        cpu.registers[A], cpu.registers[F] = (old ^ flags) & 255, flags
        cpu.registers[R], cpu.registers[IFF] = old & 255, flags & 1
        expected = cpu.registers[:]
        result = (old + 32) & 65535
        expected[H], expected[L] = result >> 8, result & 255
        expected[D], expected[E] = 0x90, 23
        expected[B], expected[C] = 0, 32
        expected[F] = ((flags & 0xC0) | ((result >> 8) & 0x28)
                       | (16 if (old & 0xFFF) + 32 > 0xFFF else 0)
                       | (1 if old + 32 > 65535 else 0))
        expected[SP], expected[PC] = 0x8000, 0x3FFF
        expected[R], expected[T] = refresh(old & 255, 53), 561
        writes = [(0x9000 + i, value) for i, value in enumerate(copied)]
        writes += [(0x6282, result & 255), (0x6283, result >> 8)]
        memory.writes = []
        memory.recording = True
        for _ in range(40):
            if cpu.registers[PC] == 0x3FFF:
                break
            cpu.run()
        else:
            raise AssertionError(('Не завершён EmitAttributeRow', old, flags))
        assert cpu.registers == expected, (old, flags, cpu.registers, expected)
        assert memory[0x9000:0x9017] == copied
        assert Counter(memory.writes) == Counter(writes), (old, flags)
        assert memory[0x7FFC:0x8000] == [0x5A, 0xC3, 255, 63]
        cases += 1

    for old in range(65536):
        check(old, (old * 37) & 255)
    for row in range(24):
        for flags in range(256):
            check(0x5820 + row * 32, flags)
    report = dict(passed=True, total_cases=cases, entire_word_domain=True,
                  all_flags_for_24_attribute_rows=True, exact_all_registers_r_t=True,
                  original_template_copied_before_operand_update=True,
                  exact_25_writes_no_stack_writes=True,
                  frame_return_word_preserved=True, destination=0x9000,
                  generated_template_executed=False, assembly_executed=False,
                  irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalEmitAttributeRowVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
