"""Три проекции слова A78F на коэффициенты третьей строки матрицы."""
from collections import Counter
import argparse,json

from CheckActionObjectOffsetVector import multiply
from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceControlsPointRespawn import refresh


def record_scale_examples():
    """Три исходных фрагмента, без выбора модели и без полного игрового кадра."""
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    stop_update = symbols['Action.UpdateRecordComponents.LoadBase1']
    functions = {row['name']: row for row in json.loads(
        (ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes()) if row['region'] == 'Action'}
    frame = functions['UpdateFrame']
    flow = next(row for row in json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
                if row['name'] == 'Action')['instructions']
    frame_rows = [row for row in flow if row['slot'] == frame['slot']
                  and frame['offset'] <= row['offset'] < frame['end_offset']]
    flat = flat_action()
    order = []
    # Проверка порядка потребителей старого вектора и последующего пересчёта.
    for name in ('UpdateObjects', 'SubtractScaledWorkVector', 'UpdateMotionFromControls'):
        target = functions[name]['address']
        calls = [row for row in frame_rows if row['operation'] == f'CALL #{target:04X}']
        assert len(calls) == 1
        site = calls[0]['address']
        assert bytes(flat[site:site + 3]) == bytes([0xCD, target & 255, target >> 8])
        order.append(dict(procedure=name, call_address=site, target=target))
    assert [row['call_address'] for row in order] == sorted(row['call_address'] for row in order)
    rows = []
    for speed, expected_product in ((20, 19), (-20, -19), (1, 0), (-1, 0)):
        for code in (1, 0x14):
            memory = flat_action()
            cpu = Simulator(memory)
            cpu.registers[:] = get_registers({'AF': 0x7F00, 'DE': speed & 65535,
                'IX': 0x3FFF, 'SP': 0xBFFE, 'PC': 0xD12C}, None, False)
            # Расчёт одной компоненты по настоящему умножителю с коэффициентом 127.
            cpu.run(start=0xD12C, stop=0x3FFF)
            product = cpu.registers[6] * 256 + cpu.registers[7]
            assert product == expected_product & 65535
            for address, value in ((0xE5B3, product), (0xE5D2, 0), (0xE5ED, 0),
                                   (0xA100, 0x1000)):
                memory[address:address + 2] = [value & 255, value >> 8]
            memory[0xA112] = code
            cpu.registers[8:10] = [0xA1, 0]
            cpu.registers[12] = 0xBFFE
            # Подготовка активного смещения, остановка до чтения заголовка модели.
            cpu.run(start=0xE55C, stop=0xE58E)
            effective = expected_product // 2 if code == 0x14 else expected_product
            active = memory[0xE5B3] | memory[0xE5B4] << 8
            assert active == effective & 65535
            assert memory[0xE5B0:0xE5B2] == [0, 0]
            # Отдельный допустимый вход e=1, HL=200, заголовок модели в этом опыте не читается.
            cpu.registers[6:8] = [0, 200]
            cpu.run(start=0xE5A4, stop=stop_update)
            component = memory[0xA100] | memory[0xA101] << 8
            assert component == 0x1000 - effective
            rows.append(dict(speed_word_signed=speed, coefficient=127, class_code=code,
                product_signed=expected_product, effective_active_signed=effective,
                initial_component=0x1000, final_component=component,
                delta_signed=component - 0x1000))
    return dict(passed=True, cases=rows, update_frame_call_order=order,
        original_multiply_entry=0xD12C,
        original_prepare_start=0xE55C, original_prepare_stop=0xE58E,
        original_update_entry=0xE5A4, original_update_stop=stop_update,
        assumed_valid_model_scale=1, explicit_phase_boundary_register_setup=True,
        model_header_selection_executed=False, full_record_update_executed=False,
        whole_frame_executed=False, physical_unit_proved=False,
        irq_executed=False, assembly_executed=False, native_execution=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rear',action='store_true');args=parser.parse_args()
    baseline = flat_action()
    memory = baseline.copy()
    memory[0xBFFE:0xC000] = [255, 63]
    if args.rear:
        for address in (0x6E75,0x6E88,0x6E9B):memory[address:address+2]=[0xED,0x44]
    sim = Simulator(memory)
    counts = Counter()

    def check(word, coefficients):
        for address, value in zip((0xCBD8, 0xCBEE, 0xCC09), coefficients):
            memory[address] = value
        memory[0xA78F:0xA791] = [word & 255, word >> 8]
        initial = get_registers({'PC': 0x6E72, 'SP': 0xBFFE, 'BC': 0x5A3C,
                                 '^AF': 0x1234, 'IX': 0xABCD, 'IY': 0x2468}, None, False)
        wanted = list(initial)
        cycles = 28
        products = []
        for coefficient in coefficients:
            value, fetches = multiply(wanted, (-coefficient)&255 if args.rear else coefficient, word)
            products.append(value)
            cycles += fetches
        wanted[8:10] = [0x6E, 0xA8]
        wanted[PC], wanted[SP], wanted[15] = 0x3FFF, 0xC000, refresh(initial[15], cycles)
        sim.registers[:] = initial
        sim.run(0x6E72, 0x3FFF)
        compared = (*range(13), 14, 15, *range(16, 25), 26, 27)
        assert all(sim.registers[i] == wanted[i] for i in compared), (
            word, coefficients, [(i, sim.registers[i], wanted[i]) for i in compared if sim.registers[i] != wanted[i]])
        for address, value in zip((0xE5B3, 0xE5D2, 0xE5ED), products):
            assert memory[address:address + 2] == [value & 255, value >> 8]
        counts['cases'] += 1

    for word in range(65536):
        check(word, (word & 255, word >> 8, (word * 73 + 17) & 255))
    report = dict(passed=True, total_cases=counts['cases'], every_input_word=True,
                  start=0x6E72, preceding_key_dispatch_executed=False, rear_NEG_pairs_executed=args.rear,
                  original_NOP_pairs_executed=not args.rear, exact_registers_flags_R_and_SP=True,
                  all_memory_side_effects_checked=False,assembly_executed=False,native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / ('Tools/Disasm/Reports/'+('ActionMotionRearTail' if args.rear else 'ActionMotionVectorTail')+'Verification.json')).write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
