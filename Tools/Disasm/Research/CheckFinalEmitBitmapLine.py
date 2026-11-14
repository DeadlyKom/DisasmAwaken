"""Выдача одного исходного шаблона для всех пар строк источника и приёмника."""
from collections import Counter
import json

from CheckFinal import ROOT, Simulator, get_registers, original_memory, screen_offset, word
from CheckPreviewCoordinateMultiply import Memory
from skoolkit.simutils import A, B, C, D, E, F, H, L, PC, R, SP, T


def main():
    memory = Memory(original_memory())
    word(memory, 0x7FFE, 0x3FFF)
    cpu = Simulator(memory)
    initial = get_registers(dict(PC=0x620E, SP=0x7FFE, AF=0xA55A,
                                HL=0x1357, DE=0x9000, BC=0x369C,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    template = memory[0x6247:0x627B]
    targets = (0x6248, 0x6262, 0x6255, 0x626F)
    cases = 0
    for source_row in range(192):
        for target_row in range(192):
            memory.recording = False
            current = (0xC000 + screen_offset(source_row),
                       0x4000 + screen_offset(target_row) + 16)
            updated = (0xC000 + screen_offset(source_row + 1),
                       0x4000 + screen_offset(target_row + 1) + 16)
            memory[0x6247:0x627B] = template
            # Несогласованные вторые половины должны скопироваться до замены операндов следующей строки.
            values = (current[0], 0x1234, current[1], 0xABCD)
            for pointer, value in zip(targets, values):
                word(memory, pointer, value)
            copied = memory[0x6247:0x627B]
            cpu.registers[:] = initial
            cpu.registers[F] = (source_row * 37 + target_row * 11) & 255
            expected = cpu.registers[:]
            final_hl = updated[1] + 16
            if target_row & 7 != 7:
                final_a = (target_row + 1) & 7
                kept = 4 if final_a.bit_count() % 2 == 0 else 0
            else:
                final_a = 16 if target_row & 56 == 56 else updated[1] >> 8
                kept = 0
            final_f = kept | ((final_hl >> 8) & 0x28)
            if (updated[1] & 0xFFF) + 16 > 0xFFF:
                final_f |= 16
            expected[A], expected[F] = final_a, final_f
            expected[B], expected[C] = 0, 16
            expected[D], expected[E] = 0x90, 52
            expected[H], expected[L] = final_hl >> 8, final_hl & 255
            expected[SP], expected[PC] = 0x8000, 0x3FFF
            writes = [(0x9000 + i, value) for i, value in enumerate(copied)]
            for pointer, value in zip(targets, (updated[0], updated[0] + 16, updated[1], final_hl)):
                writes += [(pointer, value & 255), (pointer + 1, value >> 8)]
            writes += [(0x7FFC, 0x1C), (0x7FFD, 0x62), (0x7FFC, 0x2C), (0x7FFD, 0x62)]
            memory.writes = []
            memory.recording = True
            for _ in range(120):
                if cpu.registers[PC] == 0x3FFF:
                    break
                cpu.run()
            else:
                raise AssertionError(('Не завершён EmitBitmapLine', source_row, target_row))
            assert all(cpu.registers[i] == value for i, value in enumerate(expected) if i not in (R, T)), (source_row, target_row, cpu.registers, expected)
            assert memory[0x9000:0x9034] == copied
            assert Counter(memory.writes) == Counter(writes), (source_row, target_row)
            assert memory[0x7FFE:0x8000] == [255, 63]
            cases += 1
    report = dict(passed=True, total_cases=cases, original_template_copied_before_patch=True,
                  independent_screen_geometry=True, all_192_by_192_row_pairs=True,
                  exact_registers_except_r_t=True, exact_write_multiplicity=True,
                  source_and_target_columns=[0, 16], generated_template_executed=False,
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FinalEmitBitmapLineVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
