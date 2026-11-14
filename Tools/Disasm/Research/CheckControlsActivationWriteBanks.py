"""Физические банки всех записей подготовки и активации параметров.

Документация: ../../../Docs/ControlsParameterActivation.md
Документация: ../../../Docs/ControlsTemporaryModule.md
"""
from copy import deepcopy
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckControlsParameterCallWrites import derive_report as derive_parameter_report
from CheckActionApplyParameters import DESTINATIONS


def derive_apply_routes(rows):
    # Проверка начального адреса параметров по фактическим байтам LD HL,nn.
    assert rows[0]['operation'] == 'LD HL,#9BA4' and rows[0]['hex'] == '21a49b'
    assert rows[-1]['operation'] == 'RET' and rows[-1]['hex'] == 'c9'
    pointer = 0x9BA4
    loaded = None
    reads = []
    routes = []
    for index, row in enumerate(rows[1:], 1):
        raw = bytes.fromhex(row['hex'])
        if raw == b'\x7e':
            assert row['operation'] == 'LD A,(HL)'
            loaded = pointer - 0x9BA4
            reads.append(loaded)
        elif raw == b'\x23':
            assert row['operation'] == 'INC HL'
            pointer += 1
        elif raw[0] == 0x32:
            # Расчёт физического назначения каждого прочитанного поля по операнду LD (nn),A.
            assert len(raw) == 3 and loaded is not None
            address = int.from_bytes(raw[1:], 'little')
            assert row['operation'] == 'LD (#%04X),A' % address
            routes.append((loaded, address))
        else:
            assert raw == b'\xc9' and row['operation'] == 'RET' and index == len(rows)-1
    assert reads == list(range(15)) and pointer == 0x9BB2
    assert tuple(routes) == DESTINATIONS
    return routes


def derive_report():
    preparation = derive_report_preparation()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256'] == preparation['original_disk_sha256']
    entries = {row['slot']: row for row in manifest['entries']}
    payloads = {}
    for slot in (17, 23):
        entry = entries[slot]
        payloads[slot] = (ROOT/(entry['path']+'.bin')).read_bytes()
        assert payloads[slot] == disk[entry['offset']:entry['offset']+entry['length']]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    blocks = {}
    fingerprints = {}
    # Проверка исходного хранения и реального переноса каждого из пяти исполняемых блоков.
    for region, first, end, name in [
            ('Action', 0xAB1B, 0xAB23, 'SelectMemoryPage'),
            ('Action', 0xAC5D, 0xACAB, 'ApplyParameterSet'),
            ('Action', 0xAC44, 0xAC5D, 'ActivateParameterSet'),
            ('Controls', 0xDE0A, 0xDE10, 'BuildAndActivateParameters'),
            ('Action', 0x697E, 0x6986, 'BuildBankedParameterSet')]:
        rows = [row for block in flow if block['name'] == region
                for row in block['instructions'] if first <= row['address'] < end]
        assert rows[0]['address'] == first
        for row, following in zip(rows, rows[1:] + [dict(address=end)]):
            raw = bytes.fromhex(row['hex'])
            assert row['address'] + len(raw) == following['address']
            slot = 23 if region == 'Controls' else 17
            offset = row['address'] - (0xDADE if slot == 23 else 0x6000)
            if slot == 17 and row['address'] < 0x7F8F:
                offset += 0x23D
            assert row['slot'] == slot and row['offset'] == offset
            assert payloads[slot][offset:offset+len(raw)] == raw
        raw = b''.join(bytes.fromhex(row['hex']) for row in rows)
        blocks[first] = rows
        fingerprints[region+'.'+name] = dict(entry=first, end_exclusive=end,
            original_bytes=len(raw), original_code_sha256=sha256(raw).hexdigest())
    # Проверка селектора, он записывает только сохранённый BC и передаёт A в полный порт 7FFD.
    selector = blocks[0xAB1B]
    assert [row['operation'] for row in selector] == [
        'PUSH BC', 'LD BC,#7FFD', 'OUT (C),A', 'POP BC', 'RET']
    assert ''.join(row['hex'] for row in selector) == 'c501fd7fed79c1c9'
    routes = derive_apply_routes(blocks[0xAC5D])
    # Проверка порядка выбора банка и всех сбросов после применения набора.
    assert [row['operation'] for row in blocks[0xAC44]] == [
        'LD A,#10', 'CALL #AB1B', 'CALL #AC5D', 'LD HL,#0000',
        'LD (#ECA9),HL', 'LD (#ECF6),HL', 'XOR A',
        'LD (#9B83),A', 'LD (#9B82),A', 'RET']
    assert ''.join(row['hex'] for row in blocks[0xAC44]) == (
        '3e10cd1babcd5dac21000022a9ec22f6ecaf32839b32829bc9')
    # Проверка настоящего хвостового JP, дополнительный возврат на сменяемую страницу не создаётся.
    assert ''.join(row['hex'] for row in blocks[0xDE0A]) == 'cd10dec344ac'
    assert [row['operation'] for row in blocks[0xDE0A]] == ['CALL #DE10', 'JP #AC44']
    assert ''.join(row['hex'] for row in blocks[0x697E]) == '3e11cd1babc30ade'
    assert [row['operation'] for row in blocks[0x697E]] == ['LD A,#11', 'CALL #AB1B', 'JP #DE0A']
    # Расчёт банков всех нестековых записей с учётом смены отображения перед ApplyParameterSet.
    def physical(address, page):
        assert 0x4000 <= address <= 0xFFFF
        return dict(address=address, bank=5 if address < 0x8000 else 2 if address < 0xC000 else page,
                    bank_offset=address & 0x3FFF)
    phases = [dict(name='preparation_in_bank_1', selected_upper_bank=1,
                   writes=[physical(address, 1) for address in preparation['nonstack_destinations']]),
              dict(name='apply_after_select_bank_0', selected_upper_bank=0,
                   writes=[dict(field=index, **physical(address, 0)) for index, address in routes]),
              dict(name='reset_after_apply', selected_upper_bank=0,
                   writes=[physical(address, 0) for address in (0xECA9,0xECAA,0xECF6,0xECF7,0x9B83,0x9B82)])]
    physical_set = {(row['bank'], row['bank_offset']) for phase in phases for row in phase['writes']}
    assert len(physical_set) == 50 and not any(bank == 1 for bank, _ in physical_set)
    assert all(row['address'] not in (0xDB01,0xDB02) for phase in phases for row in phase['writes'])
    # Расчёт общей глубины, CALL подготовителя добавляет два байта к его восьми, активация требует четыре.
    preparation_depth = 2 + preparation['maximum_additional_stack_bytes']
    activation_depth = 2 + 2
    assert preparation_depth == 10 and activation_depth == 4
    # Проверка каждого SP, при котором десять дополнительных байтов и внешний возврат целиком в общей RAM.
    sp_values = range(0x400A, 0xBFFF)
    for sp in sp_values:
        stack = list(range(sp - 10, sp))
        assert min(stack) >= 0x4000 and sp+1 < 0xC000
        assert all(physical(address, 1) == physical(address, 0) for address in stack + [sp,sp+1])
    # Проверка всех байтов с разрешённой записью, старшие биты не меняют фиксированные окна.
    unlocked = [value for value in range(256) if not value & 0x20]
    control_pages = [value for value in unlocked if value & 7 == 1]
    assert len(unlocked) == 128 and len(control_pages) == 16
    assert sorted({value & 0x1F for value in unlocked}) == list(range(32))
    assert sorted({value & 0x1F for value in control_pages}) == [1,9,17,25]
    for value in unlocked:
        for first in (0x697E, 0xAB1B, 0xAC44, 0xAC5D):
            for row in blocks[first]:
                assert physical(row['address'], value & 7) == physical(row['address'], 0)
        assert physical(0xDE0A, 0x11 & 7)['bank'] == 1
        assert all(physical(address, 0x10 & 7)['bank'] == 0
                   for _, address in routes if address >= 0xC000)
    # Проверка чувствительности маршрутизатора к смене назначения или добавлению косвенной записи.
    rejected = []
    for kind in ('destination', 'indirect_store', 'parameter_pointer'):
        rows = deepcopy(blocks[0xAC5D])
        if kind == 'destination':
            row = next(row for row in rows if row['hex'].startswith('32'))
            row.update(operation='LD (#DB01),A', hex='3201db')
        elif kind == 'indirect_store':
            row = next(row for row in rows if row['hex'] == '7e')
            row.update(operation='LD (DE),A', hex='12')
        else:
            rows[0].update(operation='LD HL,#DB01', hex='2101db')
        try:
            derive_apply_routes(rows)
        except AssertionError:
            rejected.append(kind)
        else:
            raise AssertionError(kind)
    return dict(passed=True, method='original_preparation_and_tail_activation_physical_write_domains',
        original_disk_sha256=manifest['sha256'], functions=fingerprints, phases=phases,
        unique_nonstack_physical_destinations=50, physical_bank_1_nonstack_writes=0,
        preparation_extra_stack_bytes=preparation_depth, activation_extra_stack_bytes=activation_depth,
        maximum_additional_stack_bytes=10,
        common_RAM_stack_start_SP_minimum=0x400A, common_RAM_stack_start_SP_maximum=0xBFFE,
        common_RAM_stack_SP_values_checked=len(sp_values),
        stack_and_external_return_have_same_physical_mapping_before_and_after_switch=True,
        upper_bank_1_unchanged_under_common_RAM_stack_preconditions=True,
        bank1_DB01_DB02_not_written_under_preconditions=True,
        DE0A_initial_unlocked_page_values=[1,9,17,25], DE0A_port_values=[0x10],
        banked_wrapper_initial_unlocked_page_values=list(range(32)), banked_wrapper_port_values=[0x11,0x10],
        DE0A_initial_unlocked_7ffd_bytes=control_pages,
        banked_wrapper_initial_unlocked_7ffd_bytes=unlocked,
        initial_7ffd_bits_7_6_do_not_change_fixed_RAM_or_upper_bank_number=True,
        DE0A_tail_does_not_return_to_bank_1=True, banked_wrapper_uses_same_external_return=True,
        unsupported_apply_mutations_rejected=rejected,
        required_preconditions=['исходные код, таблицы и перенесённое ядро ACTION',
            'для DE0A исходно выбран банк 1, для 697E начальный выбор банка произволен',
            'бит блокировки 7FFD сброшен, исходный банк 1 содержит CONTROL, банк 0 содержит ACTION',
            'внешний возврат действителен после выбора банка 0',
            'стек и внешний возврат целиком в общей RAM, без перекрытия кода, таблиц и рабочих данных',
            'IRQ, NMI, DMA и иные внешние писатели не вмешиваются'],
        all_game_callers_meet_preconditions_proved=False,
        full_program_DB01_DB02_writer_graph_proved=False, temporary_module_legitimate_entry_proved=False,
        independent_numeric_child_algorithms_reproved=False, instruction_execution_simulated=False,
        assembly_executed=False, native_execution=False)


def derive_report_preparation():
    # Проверка прежнего отчёта по заново вычисленному доказательству, файл не обновляется.
    report = derive_parameter_report()
    path = ROOT/'Tools/Disasm/Reports/ControlsParameterCallWritesVerification.json'
    assert json.loads(path.read_bytes()) == json.loads(json.dumps(report))
    return report


def main():
    result = derive_report()
    path = ROOT/'Tools/Disasm/Reports/ControlsActivationWriteBanksVerification.json'
    data = (json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes().replace(b'\r\n', b'\n') == data, 'Отчёт отличается, автоматическая замена запрещена'
    else:
        path.write_bytes(data)
    print('Пять дополнительных блоков, 50 нестековых физических адресов, банк 1 сохранён при общей рамке из 10 байтов.')


if __name__ == '__main__':
    main()
