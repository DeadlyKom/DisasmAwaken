"""ADC5..AE14, две настоящие проекции AE73, точные регистры и все записи."""
from collections import Counter
from itertools import product
import json
import random

from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckIntro import ROOT
from ReferenceActionLogRatio import LOG, EXP, evaluate


def reference(horizontal, vertical, depth):
    writes = []
    def push(address, value):
        # Модель SkoolKit регистрирует слово младшим байтом вперёд, это не порядок шинных циклов PUSH.
        writes.extend(((address, value & 255), (address + 1, value >> 8)))
    denominator = (-depth) & 65535 if depth & 32768 else depth
    push(0xBFFC, horizontal)
    push(0xBFFA, depth)
    push(0xBFF8, 0xADD5)
    first = evaluate(vertical, denominator)
    writes.extend(first['writes'])
    if first['af'][1] & 1:
        return dict(path='vertical_rejected', hl=first['hl'], de=depth, bc=first['bc'],
                    af=(1, 0), alternate_af=first['alternate_af'], writes=writes)
    y = first['hl']
    if depth & 32768:
        y = (-y) & 65535
    y = (y + 48) & 65535
    push(0xBFFC, y)
    push(0xBFFA, depth)
    push(0xBFF8, 0xADFB)
    second = evaluate(horizontal, denominator)
    writes.extend(second['writes'])
    if second['af'][1] & 1:
        return dict(path='horizontal_rejected', hl=second['hl'], de=depth, bc=second['bc'],
                    af=(1, 0), alternate_af=second['alternate_af'], writes=writes)
    x = second['hl']
    if depth & 32768:
        x = (-x) & 65535
    return dict(path='accepted', hl=(x + 128) & 65535, de=y, bc=second['bc'],
                af=(0, 0x44), alternate_af=second['alternate_af'], writes=writes)


def main():
    from ReferenceActionOverlayProjection import evaluate as projection_reference
    baseline = flat_action()
    baseline[0x9100:0x9200] = [value & 255 for value in LOG]
    baseline[0x9200:0x9300] = [value >> 8 for value in LOG]
    baseline[0x9300:0x9400] = EXP
    baseline[0xBFFE:0xC000] = [255, 63]
    memory = Memory(baseline)
    simulator = Simulator(memory)
    counts, touched = Counter(), set()
    refresh_values, full_costs = set(), set()
    def check(horizontal, vertical, depth):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = baseline[address]
        serial = counts.total()
        initial = get_registers({'PC': 0xADC5, 'SP': 0xBFFE, 'AF': serial & 65535,
                                 'HL': vertical, 'DE': depth, 'BC': horizontal,
                                 '^HL': 0x1357, '^DE': 0x2468, '^BC': 0x369C, '^AF': 0xABCD,
                                 'IX': 0xBEEF, 'IY': 0x5C3A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        expected = reference(horizontal, vertical, depth)
        wanted = list(initial)
        for position, name in ((6, 'hl'), (4, 'de'), (2, 'bc')):
            value = expected[name]
            wanted[position:position + 2] = [value >> 8, value & 255]
        wanted[0:2], wanted[16:18] = expected['af'], expected['alternate_af']
        wanted[PC], wanted[SP] = 0x3FFF, 0xC000
        # Расчёт полного M1 существующей составной моделью двух отношений и знаковых ветвей.
        composed = projection_reference(initial)
        wanted[15] = composed['registers'][15]
        refresh_values.add(initial[15]);full_costs.add(composed['refresh_m1'])
        simulator.registers[:] = initial
        memory.writes, memory.recording = [], True
        measured_m1 = 0
        for _ in range(450):
            if simulator.registers[PC] == 0x3FFF:
                break
            before_r = simulator.registers[15]
            simulator.run()
            increment = (simulator.registers[15] - before_r) & 127
            assert increment in (1, 2)
            measured_m1 += increment
        else:
            raise AssertionError(('нет возврата', horizontal, vertical, depth))
        memory.recording = False
        assert measured_m1 == composed['refresh_m1'], (horizontal, vertical, depth, measured_m1, composed['refresh_m1'])
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[index] == simulator.registers[index] for index in compared), (
            horizontal, vertical, depth, [(i, wanted[i], simulator.registers[i]) for i in compared
                                         if wanted[i] != simulator.registers[i]])
        assert memory.writes == expected['writes'], (horizontal, vertical, depth, memory.writes, expected['writes'])
        final = dict(expected['writes'])
        assert all(memory[address] == value for address, value in final.items())
        touched = set(final)
        counts[expected['path']] += 1
    # Проверка нулей, обоих знаков, границ байта и особого модуля 8000 во всех тройках.
    edges = (0, 1, 2, 127, 128, 255, 256, 257, 511, 512, 1024, 32767, 32768, 32769, 65534, 65535)
    for arguments in product(edges, repeat=3):
        check(*arguments)
    # Проверка дополнительных сочетаний, генератор и набор повторяемы.
    rng = random.Random(0xADC5)
    for _ in range(4096):
        check(*(rng.randrange(65536) for _ in range(3)))
    assert set(counts) == {'accepted', 'vertical_rejected', 'horizontal_rejected'}
    assert refresh_values == set(range(256))
    result = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  exact_registers_except_R_and_T=False, exact_registers_including_R=True,
                  full_M1_count_compared_not_only_R_modulo_128=True, all_256_initial_R_values=True,
                  observed_M1_min=min(full_costs), observed_M1_max=max(full_costs), exact_T_proved=False,
                  exact_order_of_all_memory_writes=True,
                  stack_frame_bytes=6, actual_divider_executed=True, all_joint_inputs_exhausted=False,
                  assembly_executed=False, native_execution=False, irq_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionOverlayProjectionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
