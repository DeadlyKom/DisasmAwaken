"""D694..D79F, реальные рабочий SP, самомодификация комбинаций и перспектива всех выбранных точек."""
from collections import Counter
from itertools import product
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceActionVertexGroup import group, WORD_TARGETS, BYTE_TARGETS

PACKED_INPUTS = (0xD69C, 0xD69F, 0xD6A2)
DEPTH_INPUTS = (0xD6E2, 0xD6E1, 0xD6DF)


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, reasons, touched = Counter(), Counter(), set()

    def check(words=(0x0102, 0x0304, 0x0506), thirds=(7, 8, 9), tag=255, base=(1000, 0, 0), exponent=1, offset=4):
        nonlocal touched
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        for address, value in zip(PACKED_INPUTS, words):
            memory[address], memory[address + 1] = value & 255, value >> 8
        for address, value in zip(DEPTH_INPUTS, thirds):
            memory[address] = value
        for address, value in zip((0xD7A2, 0xD7C4, 0xD9B6), base):
            memory[address], memory[address + 1] = value & 255, value >> 8
        for address in (0xD7AC, 0xD7C7, 0xD9B9):
            memory[address] = 6 - exponent
        memory[0xD699] = offset
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        serial = counts.total()
        initial = get_registers({'AF': (serial * 73) & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xAB00 | tag, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xD694}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        result = group(words, thirds, tag, base, exponent, offset, (tuple(initial[16:18]), 0x9ABC, 0x5678, 0x1234))
        wanted = list(initial)
        wanted[0:2], wanted[16:18] = result['af'], result['alt_af']
        for position, key in ((2, 'bc'), (4, 'de'), (6, 'stack'), (8, 'ix'), (10, 'iy'), (18, 'alt_bc'), (20, 'alt_de'), (22, 'alt_hl')):
            value = result[key]
            wanted[position:position + 2] = [value >> 8, value & 255]
        wanted[SP], wanted[PC] = 0xC000, 0x3FFF
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        def byte(address, value):
            bank = 2 if address < 0xC000 else 0
            expected[bank][address & 0x3FFF] = value
            writes.append((bank, address & 0x3FFF, value))
        def word(address, value):
            byte(address, value & 255)
            byte(address + 1, value >> 8)
        # Расчёт физически раздельных изменяемых операндов, отрицание пары выполняется побайтно.
        word(0xD79D, 0xBFFE)
        for index in (0, 1, 3, 2, 5, 4, 6, 7):
            word(WORD_TARGETS[index], result['words'][index])
        for index in (5, 4, 6, 7):
            byte(BYTE_TARGETS[index], result['depths'][index])
        # Запись всех вершин с сохранением частичных SavedDepth и пятого байта каждой записи.
        for stack, point in result['points']:
            if point['save_depth']:
                word(0xD9C3, point['depth'])
            word(stack - 2, point['first'])
            word(stack - 4, point['second'])
            reasons[point['reason']] += 1
        byte(0xD699, result['stack'] & 255)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(3600):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат группы', tag))
        memory.recording = False
        compared = (*range(13), 14, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (words, thirds, tag, base, exponent, offset,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), ('RAM', tag)
        touched = {(bank, index) for bank, index, value in memory.writes}
        counts['single' if tag == 1 else 'antipodes' if tag == 129 else 'mask'] += 1
    # Проверка всех кодов и независимых знаков packed-пар, разных отказов перспективы и масштаба.
    for tag in range(256):
        for exponent in range(1, 7):
            for base in ((1000, 0, 0), (0, 0, 0), (32768, 0, 0), (1, 32768, 32768)):
                check(tag=tag, exponent=exponent, base=base)
    # Проверка всех слов каждого входа по отдельному сечению, включая перенос между двумя байтами.
    for value in range(65536):
        for index in range(3):
            words = [0x1357, 0x2468, 0xACE0]
            words[index] = value
            check(tuple(words), tag=1)
    for value in range(256):
        for index in range(3):
            thirds = [0x13, 0x57, 0x9B]
            thirds[index] = value
            check(thirds=tuple(thirds))
    # Проверка всех байтов рабочего смещения, выход за штатный диапазон здесь только синтетический профиль.
    for offset in range(256):
        for tag in (0, 1, 129, 255):
            check(tag=tag, offset=offset)
    rng = random.Random(0xD694)
    for _ in range(2048):
        check(tuple(rng.randrange(65536) for _ in range(3)), tuple(rng.randrange(256) for _ in range(3)), rng.randrange(256),
              tuple(rng.randrange(65536) for _ in range(3)), rng.randrange(1, 7), 4 + 5 * rng.randrange(32))
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), projected_vertex_reasons=dict(reasons),
        method='shared_proved_packed_combinations_composed_with_action_specific_perspective_oracle',
        independent_complete_child_oracle=False, children_executed_without_stubs=True,
        exact_contract_registers_and_flags=True, refresh_and_timing_independently_checked=False,
        every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_tag_bytes_and_six_scales=True, all_three_packed_words_by_separate_slices=True, all_working_offset_bytes=True,
        per_byte_rotate_and_negative_with_word_carry_preserved=True, antipode_code_81_not_regular_mask=True,
        saved_cpu_sp_restored=True, ordinary_cpu_stack_not_written=True, unmodified_fifth_point_bytes_checked=True,
        all_joint_inputs_exhausted=False, whole_object_pass_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionVertexGroupVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
