"""D7A0..DBBC, собственная формула ACTION и исходный поразрядный делитель без подмен."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceActionPerspective import project


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    counts, scales, touched = Counter(), Counter(), set()

    def check(vertex=(0, 0, 0), base=(1000, 0, 0), exponent=1):
        nonlocal touched
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        for address, value in zip((0xD7A2, 0xD7C4, 0xD9B6), base):
            memory[address], memory[address + 1] = value & 255, value >> 8
        for address in (0xD7AC, 0xD7C7, 0xD9B9):
            memory[address] = 6 - exponent
        serial = counts.total()
        stack = 0x8E04 + 5 * (serial % 40)
        initial = get_registers({'AF': (vertex[0] << 8) | (serial & 255), 'HL': 0x3FFF,
            'DE': (vertex[2] << 8) | vertex[1], 'BC': 0x369C, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': stack, 'PC': 0xD7A0}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        result = project(vertex, base, exponent, stack, tuple(initial[16:18]), 0x9ABC)
        wanted = list(initial)
        wanted[0:2], wanted[16:18] = result['af'], result['alt_af']
        for position, key in ((18, 'alt_bc'), (20, 'alt_de'), (22, 'alt_hl')):
            value = result[key]
            wanted[position:position + 2] = [value >> 8, value & 255]
        wanted[SP], wanted[PC] = stack + 5, 0x3FFF
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        def byte(address, value):
            bank = 2 if address < 0xC000 else 0
            expected[bank][address & 0x3FFF] = value
            writes.append((bank, address & 0x3FFF, value))
        def word(address, value):
            byte(address, value & 255)
            byte(address + 1, value >> 8)
        if result['save_depth']:
            word(0xD9C3, result['depth'])
        word(stack - 2, result['first'])
        word(stack - 4, result['second'])
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(450):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError('косвенное продолжение перспективы')
        memory.recording = False
        # R и T не входят в числовой оракул делителя, входное значение R алгоритмом не читается.
        compared = (*range(13), 14, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (vertex, base, exponent, result,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), ('RAM', result)
        touched = {(bank, offset) for bank, offset, value in memory.writes}
        counts[result['reason']] += 1
        scales[exponent] += 1
    # Проверка всех слов глубины и осей на разных знаменателях, включая нулевой и высокий байт глубины.
    for value in range(65536):
        check(base=(value, 1, 1))
        check(base=(256, value, 0))
        check(base=(1, value, 0))
        check(base=(3, 0, value))
    # Проверка каждого знакового локального байта при всех шести допустимых масштабах и оборачивающихся базах.
    for exponent in range(1, 7):
        for value in range(256):
            for vertex in ((value, 0, 0), (0, value, 0), (0, 0, value)):
                for base in ((1500, 0, 0), (0, 0, 0), (32767, 32767, 32768), (65535, 65535, 65535)):
                    check(vertex, base, exponent)
    rng = random.Random(0xD7A0)
    for _ in range(4096):
        check(tuple(rng.randrange(256) for _ in range(3)), tuple(rng.randrange(65536) for _ in range(3)), rng.randrange(1, 7))
    assert set(counts) == {'accepted', 'negative_depth', 'first_axis', 'second_axis'}
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), exponents=dict(scales),
        method='action_specific_normalization_bias_complement_quotient_and_flag_oracle',
        exact_contract_registers_and_flags=True, refresh_and_timing_independently_checked=False,
        every_physical_ram_byte_and_write_multiplicity_checked=True, working_sp_and_indirect_continuation_executed=True,
        all_depth_words=True, all_first_axis_words_at_depths=[1, 256], all_second_axis_words_at_depth=3,
        all_local_bytes_at_six_scales=True, zero_numerator_high_depth_bypass_preserved=True,
        normalization_inserted_ones_bias_preserved=True, source_add_carry_in_screen_subtraction_preserved=True,
        no_preview_formula_substitution=True, all_joint_inputs_exhausted=False,
        whole_vertex_group_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionPerspectiveVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
