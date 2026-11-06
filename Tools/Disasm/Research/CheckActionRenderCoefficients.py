"""C99B..CB22, девять раздельных операндов коэффициентов, исходные табличные произведения."""
from collections import Counter
from itertools import product
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import refresh
from PreviewModelMatrixOracle import product as quarter_square, arithmetic, corrected

OUTPUTS = (0xCB38, 0xCB3A, 0xCB3C, 0xCC25, 0xCC27, 0xCC29, 0xCD22, 0xCD24, 0xCD26)


def combine(left, right, subtract=False):
    value, flag = arithmetic(left, right, subtract)
    # Проверка исходной коррекции Overflow, это отражение результата, не обычное насыщение.
    kind = 'plain' if not flag & 4 else 'negate_then_decrement' if value == 128 else 'negated'
    return (*corrected(left, right, subtract), kind)


def main():
    flat = flat_action()
    assert bytes(flat[0x9800:0x9900]) == bytes(min(i, 255 - i) ** 2 // 127 for i in range(256))
    sine = flat[0x9900:0x9A00]
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    simulator = Simulator(memory)
    flow = next(r for r in json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if r['name'] == 'Action')
    def cost(start, end):
        return sum(2 if i['hex'][:2] in ('cb', 'dd', 'ed', 'fd') else 1 for i in flow['instructions'] if start <= i['address'] < end)
    fast_cost = cost(0xC99B, 0xC9CF)
    slow_cost = cost(0xC99B, 0xC9A2) + cost(0xC9CF, 0xCB23)
    counts, corrections, touched = Counter(), Counter(), set()

    def check(phases=(0, 0, 0), mode=0, flags=255):
        nonlocal touched
        memory.recording = False
        for bank, index in touched:
            memory.banks[bank][index] = baseline[bank][index]
        for i, value in enumerate(phases):
            memory[0x9B12 + i] = value
        memory[0x9B8D] = mode
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        serial = counts.total()
        initial = get_registers({'AF': 0xA500 | flags, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xC99B}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        wanted = list(initial)
        expected = [bytearray(b) for b in memory.banks]
        writes = []
        def pair(index, value):
            wanted[index:index + 2] = [value >> 8, value & 255]
        def byte(address, value):
            expected[0][address - 0xC000] = value
            writes.append((0, address - 0xC000, value))
        if mode & 1:
            phase = phases[1]
            b, big_b = sine[phase], sine[(phase + 64) & 255]
            values = (big_b, 0, (-b) & 255, b, 0, big_b, 0, 127, 0)
            order = (0, 5, 3, 2, 6, 1, 4, 8, 7)
            pair(6, 0x9900 | phase)
            wanted[2] = phase
            wanted[0:2] = [127, 0x44]
            m1, path = fast_cost, 'single_phase'
        else:
            # Расчёт синуса и четверть-периодной выборки каждой из трёх исходных фаз.
            a, b, c = (sine[p] for p in phases)
            big_a, big_b, big_c = (sine[(p + 64) & 255] for p in phases)
            q = lambda x, y: quarter_square(x, y)[0]
            values = [0] * 9
            values[0], values[3], values[6] = q(big_c, big_b), q(b, big_c), (-c) & 255
            values[7], values[8] = q(big_c, big_a), q(big_c, a)
            combinations = (
                (1, q(q(big_b, big_a), c), q(b, a), False),
                (4, q(q(b, big_a), c), q(big_b, a), True),
                (2, q(q(big_b, a), c), q(b, big_a), True),
                (5, q(q(b, a), c), q(big_b, big_a), False))
            m1 = slow_cost
            for index, left, right, subtract in combinations:
                value, flag, kind = combine(left, right, subtract)
                values[index] = value
                corrections[str(index) + ':' + kind] += 1
                m1 -= 4 if kind == 'plain' else 1 if kind == 'negated' else 0
            _, following, low = quarter_square(q(b, a), c)
            pair(6, 0x9800 | following)
            pair(4, (c << 8) | low)
            pair(2, (a << 8) | big_a)
            pair(8, (q(big_b, big_a) << 8) | b)
            pair(10, (big_c << 8) | big_b)
            wanted[0:2] = [values[5], flag]
            order = (6, 0, 3, 1, 7, 4, 2, 8, 5)
            path = 'three_phases'
        for index in order:
            byte(OUTPUTS[index], values[index])
        wanted[SP], wanted[PC], wanted[15] = 0xC000, 0x3FFF, refresh(initial[15], m1)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(310):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError('граница коэффициентов')
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (phases, mode, flags,
            [(i, wanted[i], simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert all(a == b for a, b in zip(expected, memory.banks)) and Counter(memory.writes) == Counter(writes), (phases, 'RAM', memory.writes, writes)
        touched = {(bank, index) for bank, index, value in memory.writes}
        counts[path] += 1
    # Проверка всех фаз короткого режима и всех байтов режима, только младший разряд определяет ветвь.
    for phase in range(256):
        for mode in range(256):
            check((phase ^ 255, phase, (phase * 73) & 255), mode, flags=mode)
    # Проверка всех пар первых двух фаз при четырёх четверть-периодных значениях третьей фазы.
    for p0 in range(256):
        for p1 in range(256):
            for p2 in (0, 64, 128, 192):
                check((p0, p1, p2))
    # Проверка всех третьих фаз и совместных окрестностей смены знака и экстремума синусоиды.
    for p2 in range(256):
        for p0, p1 in product((0, 1, 63, 64, 65, 127, 128, 191, 192, 255), repeat=2):
            check((p0, p1, p2), flags=p2)
    report = dict(passed=True, total_cases=counts.total(), paths=dict(counts), correction_paths=dict(corrections),
        method='shared_proved_quarter_square_formulas_with_action_specific_register_refresh_and_write_oracle',
        arithmetic_oracle='PreviewModelMatrixOracle, no original model bytes assumed from another version',
        exact_registers_flags_refresh_sp=True, every_physical_ram_byte_and_write_multiplicity_checked=True,
        output_operands=list(OUTPUTS), output_bytes=9, no_extra_stack_frame=True, all_mode_bytes=True,
        all_first_two_phase_pairs_at_four_third_phases=True, all_third_phases_at_selected_extrema=True,
        all_joint_inputs_exhausted=False, correction_primitives_all_byte_pairs_checked=False,
        native_geometry_consumer_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionRenderCoefficientsVerification.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
