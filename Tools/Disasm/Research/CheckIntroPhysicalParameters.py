"""Сверка физических параметров и реальных читателей фаз и матриц, без сборки."""
import json
from CheckIntro import ROOT, original_memory, execute, word
from IntroPhysicalParameters import BLOCKS, render, parse


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    total = 0
    for block in BLOCKS:
        offset, length, _, _ = block
        payload = raw[offset:offset+length]
        text, labels = render(block, payload)
        assert parse(block, text) == payload
        assert min(labels.values()) == 0x6300 + offset
        total += length
    # Проверка имени запроса, тип C расположен сразу после восьми символов имени.
    assert raw[0x315:0x31E] == b'STATIONFC'
    # Проверка фактической границы 63 последовательностей, соседний байт не читается этим циклом.
    assert raw[0x363:0x36A] == bytes((20, 28, 36, 43, 49, 54, 59))
    assert raw[0x3A2] == 41
    # Проверка обеих исходных неподвижных фаз настоящей процедурой обновления.
    cases = 0
    for address in (0x662C, 0x6632):
        memory = original_memory()
        expected = bytes(memory[address:address+6])
        assert expected == bytes((0, 128, 0, 0, 0, 0))
        execute(memory, {'PC': 0x6A2C, 'HL': address})
        assert bytes(memory[address:address+6]) == expected
        cases += 1
    # Расчёт независимых матриц из полубайтов, включая обнуление первого байта писателями эффекта.
    for address in (0x6993, 0x699B):
        for clear_first in (False, True):
            memory = original_memory()
            if clear_first:
                memory[address] = 0
            source = memory[address:address+8]
            expected = [(source[column] & 240) | (source[row] & 15)
                        for row in range(8) for column in range(8)]
            execute(memory, {'PC': 0x6964, 'HL': address, 'BC': address, 'DE': 0x7000})
            assert memory[0x7000:0x7040] == expected
            cases += 1
    # Проверка числовых добавок, ни один разряд не объявляется независимым флагом.
    assert max(raw[0x962:0x98A]) == 15 and min(raw[0x962:0x98A]) == 0
    result = dict(passed=True, total_cases=cases, physical_typed_bytes=total,
                  original_blocks=len(BLOCKS), final_phases_unchanged=True,
                  attribute_matrices_independently_compared=True,
                  last_lookup_neighbour_byte_classified=False,
                  whole_initialization_executed=False, assembly_executed=False,
                  irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroPhysicalParametersVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
