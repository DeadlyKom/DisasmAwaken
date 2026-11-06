"""CB23..CEE2, композиция девяти исходных операндов и точные четверть-периодные перестановки."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import refresh
from PreviewModelMatrixOracle import product, matrix
from PreviewMatrixComposeOracle import compose
from CheckActionRenderCoefficients import combine

SCENE = ((0xCB3E, 0xCB54, 0xCB6F), (0xCB8B, 0xCBA1, 0xCBBC), (0xCBD8, 0xCBEE, 0xCC09))
MODEL = ((0xCB38, 0xCC25, 0xCD22), (0xCB3A, 0xCC27, 0xCD24), (0xCB3C, 0xCC29, 0xCD26))
OUTPUT = ((0xD5FC, 0xD61E, 0xD60D), (0xD62F, 0xD651, 0xD640), (0xD662, 0xD684, 0xD673))
MIDDLE_BLOCKS = ((0xCB53, 0xCB6E), (0xCBA0, 0xCBBB), (0xCBED, 0xCC08),
                 (0xCC41, 0xCC5D), (0xCC91, 0xCCAD), (0xCCE1, 0xCCFD))


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    flow = next(r for r in json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if r['name'] == 'Action')
    def cost(start, end):
        return sum(2 if i['hex'][:2] in ('cb', 'dd', 'ed', 'fd') else 1 for i in flow['instructions'] if start <= i['address'] < end)
    general_cost = cost(0xCB23, 0xCE06) - 3
    one_cost = cost(0xCB23, 0xCD21) - sum(cost(a, b) for a, b in MIDDLE_BLOCKS) + cost(0xCE06, 0xCE19)
    quadrant_cost = {0: cost(0xCE19, 0xCE31) + cost(0xCE62, 0xCE87),
                     64: cost(0xCE19, 0xCE34) + cost(0xCE87, 0xCEB2),
                     128: cost(0xCE19, 0xCE37) + cost(0xCEB2, 0xCEE3),
                     192: cost(0xCE19, 0xCE37) + cost(0xCE37, 0xCE62)}
    counts, corrections, touched = Counter(), Counter(), set()
    producer_cases = 0

    def check(scene, model, flags=0, angle=0, phases=None):
        nonlocal touched, producer_cases
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        memory[0x9B8D] = flags
        for index, value in enumerate(phases if phases is not None else (0, angle, 0)):
            memory[0x9B12 + index] = value
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        serial = counts.total()
        initial = get_registers({'AF': (serial * 73) & 65535, 'HL': 0x1357, 'DE': 0x247A, 'BC': 0x36C9,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xCB23}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        for row in range(3):
            for column in range(3):
                memory[SCENE[row][column]] = scene[row][column]
                memory[MODEL[row][column]] = model[row][column]
        if phases is not None:
            # Исполнение реального производителя перед потребителем, в потребитель передаются фактически записанные операнды.
            simulator.registers[:] = initial
            simulator.registers[PC] = 0xC99B
            for _ in range(310):
                if simulator.registers[PC] == 0x3FFF:
                    break
                simulator.run()
            else:
                raise AssertionError('возврат производителя')
            model = tuple(tuple(memory[a] for a in row) for row in MODEL)
            expected_model = matrix(phases, flags, flat[0x9900:0x9A00])['values']
            assert [model[row][column] for column in range(3) for row in range(3)] == list(expected_model)
            producer_cases += 1
        expected_result = compose(scene, model, flags, angle)
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        branch = expected_result['branch']
        wanted[0:2] = expected_result['af']
        wanted[10:12] = [0x9B, 0x8D]
        if branch.startswith('quadrant'):
            wanted[6] = 0x98
            m1 = cost(0xCB23, 0xCB37) + quadrant_cost[angle]
        else:
            # Расчёт точного числа M1 по пропущенным средним членам и каждому достигнутому варианту коррекции.
            one = bool(flags & 1)
            m1 = one_cost if one else general_cost
            for column in range(2 if one else 3):
                for row in range(3):
                    partial = product(scene[row][0], model[0][column])[0]
                    if not one:
                        partial, flag, kind = combine(product(scene[row][1], model[1][column])[0], partial)
                        corrections[kind] += 1
                        m1 -= 4 if kind == 'plain' else 1 if kind == 'negated' else 0
                    value, flag, kind = combine(product(scene[row][2], model[2][column])[0], partial)
                    corrections[kind] += 1
                    m1 -= 4 if kind == 'plain' else 1 if kind == 'negated' else 0
            for position, key in ((2, 'bc'), (4, 'de')):
                value = expected_result[key]
                wanted[position:position + 2] = [value >> 8, value & 255]
            wanted[6:8] = [0x98, expected_result['hl'] & 255]
            wanted[8] = expected_result['ixh']
        order = ((2, 0, 1) if branch.startswith('quadrant') else (0, 1, 2))
        for column in order:
            for row in range(3):
                address = OUTPUT[row][column]
                value = expected_result['output'][row][column]
                expected[0][address - 0xC000] = value
                writes.append((0, address - 0xC000, value))
        wanted[SP], wanted[PC], wanted[15] = 0xC000, 0x3FFF, refresh(initial[15], m1)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(650):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError('возврат композиции')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (branch, flags, angle, scene, model,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), (branch, 'RAM')
        touched = {(bank, index) for bank, index, value in memory.writes}
        counts[branch] += 1
    identity = ((127, 0, 0), (0, 127, 0), (0, 0, 127))
    # Проверка всех флаговых байтов и всех фаз ветвления, включая точные четверти и игнорируемые разряды.
    for flags in range(256):
        for angle in range(256):
            scene = tuple(tuple((angle + 17 * row + 53 * column) & 255 for column in range(3)) for row in range(3))
            check(scene, identity, flags, angle)
    # Проверка каждого байта каждого входного операнда по отдельным сечениям общей ветви.
    for position in range(18):
        for value in range(256):
            scene, model = [list(row) for row in identity], [list(row) for row in identity]
            target = scene if position < 9 else model
            index = position % 9
            target[index // 3][index % 3] = value
            check(scene, model)
    rng = random.Random(0xCB23)
    for _ in range(4096):
        scene = tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3))
        model = tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3))
        check(scene, model, rng.randrange(256), rng.randrange(256))
    # Проверка передачи коэффициентов настоящего C99B, регистровая рамка потребителя задаётся отдельно и полный кадр не моделируется.
    for _ in range(1024):
        phases = tuple(rng.randrange(256) for _ in range(3))
        flags = int(phases[0] == phases[2] == 0)
        scene = tuple(tuple(rng.choice((0, 1, 127, 128, 129, 255)) for _ in range(3)) for _ in range(3))
        check(scene, identity, flags, phases[1], phases)
    assert set(counts) == {'general', 'one_axis', 'quadrant0', 'quadrant1', 'quadrant2', 'quadrant3'}
    assert set(corrections) == {'plain', 'negated', 'negate_then_decrement'}
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), correction_paths=dict(corrections),
        method='shared_proved_functional_matrix_composition_with_action_specific_register_refresh_and_memory_oracle',
        arithmetic_oracle='PreviewMatrixComposeOracle, ACTION bytes and banking checked independently',
        real_coefficient_producer_cases=producer_cases, producer_and_consumer_register_frames_separately_initialized=True,
        exact_registers_flags_refresh_sp=True, every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_flags_and_second_phase_bytes=True, all_input_operand_bytes_by_separate_slices=True,
        one_axis_quadrants_copy_and_negate_without_table_rounding=True, original_negative_80_wrap_preserved=True,
        no_extra_stack_frame_or_ports=True, all_joint_inputs_exhausted=False,
        full_vertex_transform_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderMatrixVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
