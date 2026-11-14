"""Косвенное чтение тоннажа CNSK через выход индекса корабельной вместимости.

Документация: ../../../Docs/StationTransportTradeTables.md
Документация: ../../../Docs/StrideFive.md
"""
from hashlib import sha256
import json

from CheckIntro import ROOT


def main():
    # Проверка исходных файлов станции и LANG по полным физическим секторам.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    sources = {}
    for slot in (4,5):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        sources[slot] = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
        assert sources[slot] == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    # Проверка всей исходной последовательности, старший байт индекса обнуляется до расчёта.
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code = [row for region in flow if region['name'] == 'Text'
            for row in region['instructions'] if 0xC5F9 <= row['address'] < 0xC609]
    expected = ['LD DE,#9802','POP HL','LD H,#00','PUSH HL','ADD HL,HL',
                'ADD HL,HL','POP BC','ADD HL,BC','ADD HL,DE','LD E,(HL)','LD D,#00','RET']
    assert [row['operation'] for row in code] == expected
    raw = b''.join(bytes.fromhex(row['hex']) for row in code)
    assert raw == sources[5][0x5F9:0x609] and len(raw) == 16
    for row in code:
        assert row['slot'] == 5
        assert sources[5][row['offset']:row['offset']+len(bytes.fromhex(row['hex']))] == bytes.fromhex(row['hex'])
    # Проверка физической границы двух пятибайтовых таблиц по действующей разметке.
    layout = json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_bytes())
    ship = next(row for row in layout if row['path'] == 'Source/Station/Data/ShipTradeRows.asm')
    skimmer = next(row for row in layout if row['path'] == 'Source/Station/Data/SkimmerTradeRows.asm')
    assert (ship['slot'],ship['offset'],ship['length']) == (4,0x3802,35)
    assert (skimmer['slot'],skimmer['offset'],skimmer['length']) == (4,0x3825,20)
    assert ship['offset']+ship['length'] == skimmer['offset']
    addresses = [(0x9802+5*index)&65535 for index in range(256)]
    target_fields = {0x9825+5*index:index for index in range(4)}
    aliases = [dict(ship_index=index,address=address,skimmer_index=target_fields[address],
        field='FStationSkimmerTradeRow.Unknown00',original_value=sources[4][address-0x6000])
        for index,address in enumerate(addresses) if address in target_fields]
    assert [row['ship_index'] for row in aliases] == [7,8,9,10]
    assert addresses[6] == 0x9820 and addresses[11] == 0x9839
    # Проверка связи с прежней моделью настоящего читателя, не подмена нового расчёта исполнением CPU.
    model_path = ROOT/'Tools/Disasm/Reports/StrideFiveVerification.json'
    model = json.loads(model_path.read_bytes())
    assert model['passed'] and model['accessor_cases']['0xc5f9'] == 65536
    for key in ('all_byte_indices','all_initial_flags','index_high_byte_discarded',
                'physical_disk_and_sector_hashes_checked','exact_CPU_write_sequence_checked'):
        assert model[key]
    result = dict(passed=True,method='original_reader_instructions_and_adjacent_physical_table_domains',
        original_disk_sha256=manifest['sha256'],reader_entry=0xC5F9,reader_original_hex=raw.hex(),
        reader_original_code_sha256=sha256(raw).hexdigest(),all_byte_indices_derived=256,
        ship_base=0x9802,ship_rows=7,skimmer_base=0x9825,skimmer_rows=4,row_stride=5,
        aliases=aliases,previous_CPU_model=model_path.relative_to(ROOT).as_posix(),
        previous_CPU_model_sha256=sha256(model_path.read_bytes()).hexdigest(),
        current_reader_has_no_table_count_check=True,
        conditional_current_reader_of_all_four_Unknown00_proved=True,
        ordinary_ship_selection_reaches_indices_7_to_10_proved=False,
        actual_skimmer_purchase_or_capacity_use_proved=False,
        unknown_speed_fields_purpose_proved=False,CPU_execution_performed_by_this_check=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ShipCapacitySkimmerAliasVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Индексы корабельного читателя 7..10 читают Unknown00 четырёх CNSK, штатная достижимость не утверждается.')


if __name__ == '__main__':
    main()
