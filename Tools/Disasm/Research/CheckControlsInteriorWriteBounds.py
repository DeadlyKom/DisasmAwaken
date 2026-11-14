"""Границы записей заливки, включая самомодификацию и отдельную CPU-рамку.

Документация: ../../../Docs/ControlsInteriorRows.md
Документация: ../../../Docs/ControlsTemporaryModule.md
"""
from copy import deepcopy
from hashlib import sha256
import json

from CheckIntro import ROOT


def check_layout(rows):
    code = {row['address']: bytes.fromhex(row['hex']) for row in rows}
    assert len(code) == len(rows)
    def raw(first, end):
        part = [row for row in rows if first <= row['address'] < end]
        assert part[0]['address'] == first
        for row, following in zip(part, part[1:] + [dict(address=end)]):
            assert row['address'] + len(bytes.fromhex(row['hex'])) == following['address']
        return b''.join(bytes.fromhex(row['hex']) for row in part)
    # Проверка двух внешних обёрток, исходный A возвращается из C до выбора направления.
    assert raw(0xD208,0xD211).hex() == '4f3a8cd1a779c38ad5'
    assert raw(0xD211,0xD21A).hex() == '4f3a8cd1a779c395d5'
    # Проверка самостоятельного подготовителя без записей RAM.
    assert raw(0xD57B,0xD58A).hex() == '3a8cd1a77de6e0f6015f0eff0600c9'
    # Проверка обеих настроек, они меняют операнд шага, операнд CP и код JR.
    assert raw(0xD58A,0xD595).hex() == '21e0ff22b5d52180381809'
    assert raw(0xD595,0xD59E).hex() == '21200022b5d5218c30'
    assert raw(0xD59E,0xD5B7).hex() == '2200d6d5f56f26042929292929111f0019c505042851112000'
    assert raw(0xD5B7,0xD5BA).hex() == '4ddd7d'
    # Проверка всех тридцати пар, DEC L не меняет H, запись происходит после уменьшения L.
    assert raw(0xD5BA,0xD5F6) == b'\x2d\x77' * 30
    # Проверка восстановления правого края, прибавления шага, предела и баланса трёх PUSH/POP.
    assert raw(0xD5F6,0xD609).hex() == '6919dd7dddacdd6f7cfe00300210b2c1f1d1c9'
    assert code[0xD58D] == code[0xD598] == bytes.fromhex('22b5d5')
    assert code[0xD59E] == bytes.fromhex('2200d6')
    return dict(own_raster_store_pcs=list(range(0xD5BB,0xD5F6,2)),
                code_patch_addresses=[0xD5B5,0xD5B6,0xD600,0xD601],
                stack_byte_depths=list(range(1,7)), initial_H=code[0xD5A4][1])


def address_model(y, count, upward, initial_h=4):
    # Расчёт исходного правого края по пяти ADD HL,HL и прибавлению 001F.
    hl = (((initial_h << 8) | y) * 32 + 31) & 65535
    addresses = set()
    rows = []
    if count == 0:
        return addresses, rows, hl
    for _ in range(count):
        rows.append(hl)
        low = hl & 255
        # Расчёт тридцати адресов с восьмибитным DEC L, высокий байт не заимствуется.
        for _ in range(30):
            low = (low - 1) & 255
            addresses.add((hl & 0xFF00) | low)
        hl = (hl + (-32 if upward else 32)) & 65535
        # Проверка исходного CP и изменённого кода JR до уменьшения B через DJNZ.
        reached_boundary = (hl >> 8 < 0x80) if upward else (hl >> 8 >= 0x8C)
        if reached_boundary:
            break
    return addresses, rows, hl


def derive_report():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(row for row in manifest['entries'] if row['slot'] == 22)
    payload = (ROOT/(entry['path']+'.bin')).read_bytes()
    assert payload == disk[entry['offset']:entry['offset']+entry['length']]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    rows = [row for region in flow if region['name'] == 'Controls'
            for row in region['instructions']
            if 0xD208 <= row['address'] < 0xD21A or 0xD57B <= row['address'] < 0xD609]
    # Проверка каждой физической команды в исходном CONTROL, без сборки и генерации кода.
    for row in rows:
        raw = bytes.fromhex(row['hex'])
        assert row['slot'] == 22 and row['offset'] == row['address'] - 0xC000
        assert payload[row['offset']:row['offset']+len(raw)] == raw
    layout = check_layout(rows)
    union = set()
    cases = 0
    # Проверка всех допустимых начальных строк и каждого байтового количества в обоих направлениях.
    for upward in (True, False):
        for y in range(96):
            for count in range(256):
                written, row_ends, final_hl = address_model(y,count,upward,layout['initial_H'])
                n = min(count, y+1 if upward else 96-y)
                assert len(row_ends) == n and len(written) == 30*n
                assert final_hl == 0x8000+32*y+31+(-32 if upward else 32)*n
                assert all(0x8000 <= address < 0x8C00 and 1 <= address % 32 <= 30 for address in written)
                assert all(end & 31 == 31 and end & 255 >= 31 for end in row_ends)
                union.update(written)
                cases += 1
    expected = {0x8000+32*y+column for y in range(96) for column in range(1,31)}
    assert union == expected and len(union) == 2880 and cases == 49152
    assert not (union | set(layout['code_patch_addresses'])) & {0xDB01,0xDB02}
    # Проверка чувствительности адресного вывода к ложной базе, она достигает длины временного модуля.
    wrong, _, _ = address_model(0,41,True,initial_h=7)
    assert 0xDB01 in wrong and 0xDB02 in wrong
    # Проверка отказа при изменении порядка записи и подмене проверяемого кода перехода.
    rejected = []
    for pc, replacement, name in [(0xD5BA,'24','DEC_L_replaced_by_INC_H'),
                                   (0xD601,'1802','conditional_boundary_replaced_by_JR')]:
        mutated = deepcopy(rows)
        next(row for row in mutated if row['address'] == pc)['hex'] = replacement
        try:
            check_layout(mutated)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    # Расчёт пересечений только дополнительной рамки, она не исключается без условия на SP.
    stack_overlap_sp = sorted({(address+depth)&65535 for address in (0xDB01,0xDB02) for depth in range(1,7)})
    assert stack_overlap_sp == list(range(0xDB02,0xDB09))
    return dict(passed=True, method='original_layout_and_complete_row_count_address_domains',
        original_disk_sha256=manifest['sha256'], original_code_sha256=sha256(
            b''.join(bytes.fromhex(row['hex']) for row in rows)).hexdigest(),
        original_instruction_count=len(rows), original_code_bytes=sum(len(bytes.fromhex(row['hex'])) for row in rows),
        full_wrapper_entries=[0xD208,0xD211], direct_direction_entries=[0xD58A,0xD595],
        preparation_entry_without_RAM_writes=0xD57B, domains=layout,
        all_start_row_and_count_pairs_both_directions=cases, raster_destination_count=len(union),
        raster_address_minimum=min(union), raster_address_maximum=max(union),
        raster_physical_bank=2, code_patch_physical_bank=1,
        raster_and_code_patch_destinations_disjoint_from_DB01_DB02=True,
        zero_count_still_writes_four_code_bytes_and_six_stack_bytes=True,
        initial_H_7_probe_reaches_DB01_DB02=True, unsupported_layout_mutations_rejected=rejected,
        stack_overlap_input_SP=stack_overlap_sp,
        required_preconditions=['A=0..95 и B=0..255 при входе через обёртку или выбор направления',
            'банк 1 содержит исходный CONTROL, исходные команды не меняются извне',
            'код, растр и шесть байтов рамки с внешним возвратом доступны и не перекрываются',
            'IRQ, NMI и иные внешние писатели не вмешиваются'],
        arbitrary_direct_PrepareRows_and_FillRow_entries_proved=False,
        all_game_callers_and_stack_placements_proved=False,
        all_temporary_module_length_writers_excluded=False,
        full_CPU_register_execution_or_bus_timing_simulated=False,
        assembly_executed=False, native_execution=False)


def main():
    result = derive_report()
    path = ROOT/'Tools/Disasm/Reports/ControlsInteriorWriteBoundsVerification.json'
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes().replace(b'\r\n',b'\n') == data, 'Отчёт отличается, автоматическая замена запрещена'
    else:
        path.write_bytes(data)
    print('49152 пары строки/количества, 30 писателей, 2880 байтов растра и 4 байта кода, стек отделён.')


if __name__ == '__main__':
    main()
