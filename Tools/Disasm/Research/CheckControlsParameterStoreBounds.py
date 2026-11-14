"""Статические границы собственных записей BuildParameterTables, независимо от зерна.

Документация: ../../../Docs/ControlsTemporaryModule.md
Документация: ../../../Docs/ControlsParameterTables.md
"""
from copy import deepcopy
from hashlib import sha256
import json
import re

from CheckIntro import ROOT


def literal(operation, register):
    match = re.fullmatch('LD '+register+r',#([0-9A-F]+)', operation)
    assert match, operation
    return int(match[1], 16)


def derive_domains(rows):
    code = {row['address']: row['operation'] for row in rows}
    ordered = sorted(code)

    def segment(first, last):
        return [code[pc] for pc in ordered if first <= pc <= last]

    # Проверка единственной инициализации IX и счётчика перед циклом полей.
    parameter_base = literal(code[0xDE39], 'IX')
    field_count = literal(code[0xDE3D], 'A') or 256
    assert code[0xDE3F] == "EX AF,AF'"
    # Проверка тела вычисления, оно не изменяет IX, альтернативный AF и память.
    assert segment(0xDE40, 0xDE68) == [
        'LD A,(HL)', 'AND A', 'JP P,#DE51', 'NEG', 'DEC A', 'JR Z,#DE59',
        'LD B,A', 'XOR A', 'SUB C', 'DJNZ #DE4C', 'JR #DE59', 'DEC A',
        'JR Z,#DE59', 'LD B,A', 'XOR A', 'ADD A,C', 'DJNZ #DE56',
        'INC HL', 'LD B,(HL)', 'RR B', 'JR C,#DE63', 'SRA A', 'JR #DE5B',
        'DEC HL', 'DEC HL', 'ADD A,(HL)', 'EX DE,HL', 'ADD A,(HL)', 'EX DE,HL']
    # Проверка единственной записи, шага IX и восстановления независимого счётчика.
    assert segment(0xDE69, 0xDE75) == [
        'LD (IX+#00),A', 'INC DE', 'INC IX', 'INC HL', 'INC HL', 'INC HL', 'INC HL',
        "EX AF,AF'", 'DEC A', 'JP NZ,#DE3F']
    # Проверка возврата к исходной паре HL/DE после двух временных EX DE,HL.
    assert segment(0xDE36, 0xDE36) == ['LD HL,#DF65']
    slopes = [0xDF65+3*index for index in range(field_count)]
    masks = [address+1 for address in slopes]
    parameters = [(parameter_base+index)&65535 for index in range(field_count)]
    # Проверка восстановления наборов до присваивания фиксированных выходных HL и BC.
    assert segment(0xDE78, 0xDE80) == [
        'EXX', 'POP BC', 'EXX', 'POP DE', 'LD HL,#DEDC', 'ADD HL,DE', 'EX DE,HL']
    row_base = literal(code[0xDE81], 'HL')
    stride = literal(code[0xDE84], 'BC')
    extra_rows = literal(code[0xDE8C], 'B') or 256
    assert segment(0xDE87, 0xDE8B) == ['LD A,(DE)', 'LD (HL),A', 'ADD HL,BC', 'INC DE', 'EXX']
    # Проверка переключения пар, счётчик B отделён от пары BC с физическим шагом строк.
    assert segment(0xDE8E, 0xDE99) == [
        'EXX', 'LD A,(DE)', 'EXX', 'ADD A,C', 'EXX', 'LD (HL),A',
        'ADD HL,BC', 'INC DE', 'EXX', 'DJNZ #DE8E', 'RET']
    row_addresses = [(row_base+stride*index)&65535 for index in range(extra_rows+1)]
    return dict(parameter_addresses=parameters, first_row_address=row_addresses[0],
        other_row_addresses=row_addresses[1:], coefficient_shift_mask_addresses=masks,
        field_count=field_count, extra_rows=extra_rows, row_stride=stride,
        field_counter_isolated_in_alternate_AF=True,
        row_counter_and_row_stride_in_different_EXX_sets=True)


def main():
    # Проверка всех исходных команд функции и физических секторов оригинального CONTROL.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(row for row in manifest['entries'] if row['slot'] == 23)
    control = (ROOT/(entry['path']+'.bin')).read_bytes()
    assert control == disk[entry['offset']:entry['offset']+entry['length']]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    rows = [row for region in flow if region['name'] == 'Controls'
            for row in region['instructions'] if 0xDE10 <= row['address'] < 0xDE9A]
    raw = b''.join(bytes.fromhex(row['hex']) for row in rows)
    assert len(raw) == 138 and control[0x332:0x3BC] == raw
    for row in rows:
        assert row['slot'] == 23
        assert control[row['offset']:row['offset']+len(bytes.fromhex(row['hex']))] == bytes.fromhex(row['hex'])
    proof = derive_domains(rows)
    assert proof['parameter_addresses'] == list(range(0x9BA4,0x9BB3))
    assert proof['first_row_address'] == 0x7B97
    assert proof['other_row_addresses'] == [0x7B97+6*index for index in range(1,9)]
    # Проверка ненулевых масок, каждый внутренний цикл RR достигает единицы за восемь шагов.
    masks = []
    for address in proof['coefficient_shift_mask_addresses']:
        value = control[address-0xDADE]
        assert value and value & (value-1) == 0
        masks.append(value)
    destinations = set(proof['parameter_addresses']+proof['other_row_addresses']+[proof['first_row_address']])
    assert len(destinations) == 24 and not destinations & {0xDB01,0xDB02}
    # Проверка чувствительности доказательства к сдвигу каждого из двух выходных указателей.
    mutated = deepcopy(rows)
    next(row for row in mutated if row['address'] == 0xDE39)['operation'] = 'LD IX,#DB01'
    assert 0xDB01 in derive_domains(mutated)['parameter_addresses']
    mutated = deepcopy(rows)
    next(row for row in mutated if row['address'] == 0xDE81)['operation'] = 'LD HL,#DAD1'
    assert 0xDB01 in derive_domains(mutated)['other_row_addresses']
    # Проверка отказа при появлении неизвестной операции над IX внутри тела вычисления.
    mutated = deepcopy(rows)
    next(row for row in mutated if row['address'] == 0xDE67)['operation'] = 'ADD IX,DE'
    try:
        derive_domains(mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError('Неизвестное изменение IX ошибочно признано безопасным')
    result = dict(passed=True, method='original_instruction_counter_and_pointer_invariants',
        original_disk_sha256=manifest['sha256'], original_code_sha256=sha256(raw).hexdigest(),
        original_code_bytes=len(raw), original_instruction_count=len(rows),
        function='Controls.BuildParameterTables.Entry', entry=0xDE10,
        domains=proof, original_shift_masks=masks,
        own_indirect_store_pcs=[0xDE69,0xDE88,0xDE93],
        three_own_stores_disjoint_from_DB01_DB02=True,
        store_addresses_independent_of_seed_group_middle_index_and_arithmetic_values=True,
        own_loop_bodies_do_not_write_code_or_coefficients=True,
        shifted_parameter_and_row_base_probes_detected=True,
        unsupported_inner_IX_change_rejected=True,
        required_preconditions=['вход через Entry и возврат BuildSeededIndices',
            'исходные команды и коэффициенты не изменяются извне',
            'банк 1 выбран, стек не перекрывает код и коэффициенты, IRQ не вмешиваются'],
        child_seed_rng_and_explicit_688B_store_and_stack_writes_excluded=True,
        all_callers_satisfy_preconditions_proved=False, hardware_irq_writes_proved=False,
        whole_control_length_writer_excluded=False, nonzero_length_writer_proved=False,
        assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsParameterStoreBoundsVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Три собственных места записи, 15 байтов Parameters и 9 ClassLimits, DB01/DB02 исключены при указанных предусловиях.')


if __name__ == '__main__':
    main()
