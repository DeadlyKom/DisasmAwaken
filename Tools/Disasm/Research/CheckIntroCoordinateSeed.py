"""Исходная половина координатной таблицы и реальный зеркальный построитель 69B6."""
import json
import math

from CheckIntro import ROOT, original_memory, execute


def main():
    source = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()[256:512]
    assert len(source) == 256 and source[128:] == bytes(128)
    # Проверка числового описания всех сохранённых отсчётов, это не утверждение об исходном инструменте автора.
    assert list(source[:128]) == [round(127.5 * (1 + math.cos(math.pi * index / 128))) for index in range(128)]
    cases = 0
    for context in (0, 0x55, 255):
        memory = original_memory()
        assert bytes(memory[0x6400:0x6500]) == source
        expected = list(memory)
        for index in range(129, 256):
            expected[0x6400 + index] = source[256 - index]
        for index in range(32):
            y = 4 * index
            address = 0x4000 | ((y & 192) << 5) | ((y & 7) << 8) | ((y & 56) << 2)
            expected[0x6002 + 4 * index] = expected[0x6102 + 4 * index] = address & 255
            expected[0x6003 + 4 * index] = address >> 8
            expected[0x6103 + 4 * index] = (address >> 8) + 2
        sim, _ = execute(memory, {'PC': 0x69B6, 'AF': context * 257, 'BC': 0xA500 | context})
        assert memory == expected
        assert sim.registers[2:8] == [0, context, 0x61, 0x80, 0x60, 0x80]
        cases += 1
    result = dict(passed=True, total_cases=cases, physical_seed_bytes=256,
                  stored_half_samples=128, initially_zero_second_half_preserved=True,
                  sample_description='round(127.5*(1+cos(pi*i/128))), i=0..127',
                  author_generation_method_proved=False, actual_mirror_builder_executed=True,
                  full_memory_after_mirroring_and_screen_tables_compared=True,
                  untouched_centre_index=128, mirrored_indices=[129,255],
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroCoordinateSeedVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
