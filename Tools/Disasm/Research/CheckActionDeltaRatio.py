"""AE15..AE23 с настоящим продолжением AE24 и делителем, две разности modulo 65536."""
from collections import Counter
from itertools import product
import json
import random

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckControlsComponentCompare import logical_flags
from ReferenceActionLogRatio import LOG, EXP
from ReferenceActionSignedRatioCode import evaluate
from ReferenceControlsPointRespawn import refresh


def main():
    baseline = flat_action()
    baseline[0x9100:0x9200] = [value & 255 for value in LOG]
    baseline[0x9200:0x9300] = [value >> 8 for value in LOG]
    baseline[0x9300:0x9400] = EXP
    baseline[0xBFFE:0xC000] = [255, 63]
    table = bytes(baseline[0x9A00:0x9B00])
    memory, counts, touched = Memory(baseline), Counter(), set()
    simulator = Simulator(memory)
    def check(first, first_base, second, second_base):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = baseline[address]
        denominator, numerator = (first - first_base) & 65535, (second - second_base) & 65535
        result = evaluate(numerator, denominator, table)
        serial = counts.total()
        initial = get_registers({'PC': 0xAE15, 'SP': 0xBFFE, 'HL': first, 'DE': first_base, 'BC': second_base,
                                 'AF': (serial * 73) & 65535, '^HL': second, '^DE': 0x5678,
                                 '^BC': 0x9ABC, '^AF': (serial * 109) & 65535, 'IX': 0xABCD, 'IY': 0x5C3A}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        expected = list(initial)
        for position, key in ((6, 'hl'), (4, 'de'), (2, 'bc')):
            expected[position:position + 2] = [result[key] >> 8, result[key] & 255]
        expected[0:2], expected[16:18] = result['af'], result['alternate_af']
        expected[PC], expected[SP] = 0x3FFF, 0xC000
        expected[15] = refresh(initial[15], 15 + result['refresh_m1'])
        sign = (numerator >> 8) ^ (denominator >> 8)
        writes = []
        for address, value in ((0xBFFC, (sign << 8) | logical_flags(sign)), (0xBFFA, denominator), (0xBFF8, 0xAE36)):
            writes.extend(((address, value & 255), (address + 1, value >> 8)))
        writes.extend(result['writes'])
        simulator.registers[:] = initial
        memory.writes, memory.recording = [], True
        for _ in range(500):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError('нет возврата кодирования двух разностей')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(expected[index] == simulator.registers[index] for index in compared)
        assert memory.writes == writes
        final = dict(writes)
        assert all(memory[address] == value for address, value in final.items())
        touched = set(final)
        counts[result['path']] += 1
    # Проверка обоих знаков, нулей и переходов через границу слова в каждой из четырёх исходных координат.
    edges = (0, 1, 255, 256, 32767, 32768, 32769, 65535)
    for values in product(edges, repeat=4):
        check(*values)
    rng = random.Random(0xAE15)
    for _ in range(4096):
        check(*(rng.randrange(65536) for _ in range(4)))
    result = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  actual_fallthrough_encoder_and_divider_executed=True,
                  exact_registers_including_R=True, every_memory_write_checked=True,
                  complete_four_word_input_product_exhausted=False, runtime_caller_found=False,
                  assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionDeltaRatioVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
