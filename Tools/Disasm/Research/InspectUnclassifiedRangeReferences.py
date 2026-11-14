"""Приоритеты оставшихся физических диапазонов, числовое совпадение не является доказательством обращения."""
from bisect import bisect_left
from collections import defaultdict
import argparse,hashlib,json,os,re,tempfile
from pathlib import Path
from CheckIntro import ROOT


FIXED_WINDOW_COMPANIONS = {
    4: ('Text', 'Map', 'Help', 'D3D', 'StationBoot', 'StationExit'),
    17: ('Controls', 'Voxel', 'ThreeD', 'ActionBoot'),
}


LITERAL_GROUPS = (
    ('Station', 'd3d_bank4',
     ((0x636F, 'LD (#F4C4),A'), (0x6383, 'LD (#F544),A'), (0x6386, 'LD (#F548),A'))),
    ('Station', 'io_port',
     ((0x65C1, 'LD BC,#FADF'), (0x65DF, 'LD BC,#FBDF'), (0x9B2E, 'LD BC,#FFFD'), (0x9B68, 'LD BC,#FFFD'))),
    ('Station', 'numeric_value',
     ((0xAB57, 'LD HL,#FDE8'), (0x6863, 'LD HL,#FFE0'), (0x9DBE, 'LD HL,#FFF0'),
      (0x9E30, 'LD HL,#FFF0'), (0x7C44, 'LD BC,#FFFB'), (0x646B, 'LD DE,#FFFC'), (0xC21F, 'LD DE,#FFFF'))),
    ('Action', 'object_array_before_first',
     tuple((pc, 'LD IY,#A0C0') for pc in (0xE66D, 0xE6ED, 0xE70D, 0xE729, 0xE745, 0xE98D, 0xE9A1))
     + ((0xF729, 'LD IX,#A0C0'),)
     + tuple((pc, 'LD HL,#A0C1') for pc in (0x62D1, 0x7246, 0x74AE, 0xEA77, 0xF4A9))),
    ('Action', 'voxel_bank3', ((0x6E1E, 'CALL #FA3A'),)),
    ('Action', 'numeric_value',
     ((0xD520, 'LD DE,#FF00'), (0x6C7E, 'LD DE,#FFAA'), (0xE7B2, 'LD HL,#FFB0'),
      (0x734C, 'LD BC,#FFCE'), (0x736A, 'LD BC,#FFCE'), (0x7388, 'LD BC,#FFCE'),
      (0x6768, 'LD BC,#FFD0'), (0xEAD6, 'LD BC,#FFEB'), (0x72B1, 'LD DE,#FFFF'),
      (0xB121, 'LD BC,#FFFF'), (0xD111, 'LD HL,#FFFF'), (0xE7B8, 'LD DE,#FFFF'))),
    ('Action', 'stack_top_before_push', ((0xD5C3, 'LD SP,#FFE0'),)),
    ('Action', 'io_port', ((0xECAF, 'LD BC,#FFFD'), (0xECFC, 'LD BC,#FFFD'))),
    ('Action', 'candidate_list_before_first',
     tuple((pc, 'LD HL,#A01B') for pc in (0x64C5, 0xE9C7, 0xEA1C))),
    ('Action', 'controls_bank1', ((0x6B0D, 'CALL #CEFA'), (0x6C86, 'CALL #CEFA'))),
    ('Action', 'object3d_bank4', ((0xA9AE, 'LD (#D1BA),A'),)),
    ('Controls', 'object_array_before_first',
     ((0xDDAF, 'LD IY,#A0C0'), (0xE291, 'LD IX,#A0C0'), (0xEA04, 'LD IX,#A0C0'))),
    ('Map', 'stored_map_points_before_first', ((0xC40F, 'LD IX,#9905'),)),
)


def add_literal_contexts(result):
    known = {(region, address, operation): kind
             for region, kind, sites in LITERAL_GROUPS for address, operation in sites}
    counts = defaultdict(int)
    for row in result['entries']:
        for ref in row['candidate_literal_references']:
            key = ref['region'], ref['address'], ref['operation']
            ref['use_context'] = known.get(key, 'unresolved')
            counts[ref['use_context']] += 1
    result['literal_use_contexts'] = dict(counts)
    result['unresolved_literal_candidates'] = counts['unresolved']


def document_text(result):
    lines=['# Оставшиеся физические диапазоны','',
        'Это список текущих неизвестных, не результат их смысловой классификации. Числовое совпадение внутри той же зарегистрированной области даёт только кандидата обращения. Константа может не быть адресом, возможны другие банки и косвенные обращения. Отсутствие кандидатов не означает неиспользуемость.','',
        '[Проверка](../Tools/Disasm/Research/InspectUnclassifiedRangeReferences.py), [полный реестр кандидатов](../Tools/Disasm/Reports/UnclassifiedRangeReferences.json). Адресные контексты взяты из зарегистрированных блоков переноса, параметр каталога не используется вместо пути загрузки.','',
        f"Число диапазонов {result['ranges']}, объём {result['unclassified_bytes']} байт. Список привязан к SHA256 SourceMap `{result['source_map_sha256']}` и требует пересчёта после изменения разметки.",'',
        '| Слот | Смещение файла | Байтов | Числовых кандидатов | Ресурс |','|---|---|---|---|---|']
    for row in result['entries']:
        path=row['path'];lines.append(f"| {row['slot']} | {row['offset']:04X} | {row['length']} | {row['candidate_reference_count']} | [{path.rsplit('/',1)[-1]}](../{path}) |")
    if 'byte_contents' in result:
        contents = result['byte_contents']
        lines.extend(('', '## Фактическое заполнение неизвестных диапазонов', '',
            f"Полностью нулевых диапазонов {contents['all_zero_ranges']}, они занимают {contents['all_zero_range_bytes']} байтов. "
            f"Ещё {contents['ranges_containing_nonzero_bytes']} диапазонов занимают {contents['mixed_or_nonzero_range_bytes']} байта, "
            f"из которых {contents['nonzero_bytes']} ненулевых и {contents['zero_bytes_in_nonzero_ranges']} нулевых.", '',
            'Каждый ресурс сверяется не только с SHA256 разметки, но и непосредственно с оригинальным TRD по физическому смещению записи каталога. '
            'Поле nonzero_file_bytes реестра перечисляет файловое смещение и значение каждого ненулевого байта. '
            'Одинаковые байты разных SAVE учитываются отдельно, поскольку это разные физические диапазоны.', '',
            'Нулевое заполнение не доказывает резерв, выравнивание, отсутствие чтений либо возможность удаления. '
            'Классификация всех перечисленных диапазонов остаётся неизвестной. '
            'Кроме них сохраняются открытые игровые связи уже распознанных форматов, '
            'перечисленные в [границах разбора ресурсов](ResourceSemanticLimits.md).'))
    if 'literal_use_contexts' in result:
        lines.extend(('', '## Что означают числовые совпадения', '',
            f"Из {sum(result['literal_use_contexts'].values())} совпадений без установленного контекста осталось {result['unresolved_literal_candidates']}.",
            'Записи по F4C4, F544 и F548 относятся к [предпросмотру D3D в банке 4](PreviewFaceFill.md).',
            'Вызовы FA3A и CEFA выбирают [VOXAL в банке 3](ActionVisualEffectWalk.md) и [CONTROL0 в банке 1](ProjectedBodyEntry.md).',
            'Запись по D1BA относится к [OBJECT3D в банке 4](ActionBank4Writes.md).',
            'Загрузки A0C0/A0C1 и A01B задают адреса перед [записями объектов](ActionRecordIterator.md) и [списком кандидатов](ActionCandidateList.md), чтение начинается после прибавления шага.',
            *(('Для фиксированных окон STATIONF и ACTION дополнительно проверены связанные модули. MAP загружает 9905 перед первой [точкой карты](StoredMapPoints.md), CONTROL начинает обход записей перед A100.',)
              if result.get('fixed_window_companions_checked') else ()),
            'FFE0 в SP является верхней границей [временного стека заливки](ActionPolygonFill.md), PUSH записывает байты по FFDE и FFDF.',
            'Остальные операнды задают порты ввода-вывода, числовые пределы, маски и арифметические поправки.', '',
            'Эта сверка относится к указанным инструкциям. Она оставляет открытыми косвенные обращения и другие банки. Например, принудительный нечётный индекс копировщика может читать байты после списка кандидатов в снимке ACTION. [Условия модели](ActionObjectStreamStorage.md)', '',
            'В LANG подтверждены [вычисляемые чтения четырёх байтов после станционной таблицы количеств](SecondaryContextAliases.md) с заданными индексами и состоянием. Их штатное использование и исходное назначение полей остаются открытыми.', '',
            'Для нулевых хвостов ACTION и STATIONF [сверены архивные границы и запись в банк 0](ActionArchivedFileEnd.md). Результат относится к загрузке, назначение отдельных диапазонов в игре остаётся открытым.', '',
            'Для 41 байта после упакованного экрана AWAKEN подтверждены перенос, первые перезаписи исходного окна и совпадающая копия в дистрибутивном SCL. [Жизненный цикл хвоста](IntroScreenResources.md#исходное-окно-после-переноса)', '',
            'Четыре остаточных диапазона FINALF проверены при всех фазах первого IRQ и задержках второго вывода для двух периодов модели. Обращений к ним не было. [Трасса фаз](FinalCycle.md#все-фазы-входного-прерывания)'))
    if result.get('object_table_alignment_classified'):
        lines.extend(('', 'По `#9DBD..#9DFF` ACTION подтверждены 67 байтов выравнивания перед таблицей указателей. [Сверка с авторским макросом](ActionObjectPointers.md#выравнивание-таблицы)'))
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--refresh',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    reports=ROOT/'Tools/Disasm/Reports'
    source_map_bytes=(reports/'SourceMap.json').read_bytes();source_map=json.loads(source_map_bytes)
    inventory=json.loads((reports/'Inventory.json').read_text('utf-8'))
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert len(original)==manifest['size'] and hashlib.sha256(original).hexdigest()==manifest['sha256']
    disk_entries={entry['slot']:entry for entry in manifest['entries']}
    flow=json.loads((reports/'ControlFlow.json').read_text('utf-8'))
    functions=json.loads((reports/'Functions.json').read_text('utf-8'))
    by_region={}
    for region in flow:
        values=defaultdict(list)
        for item in region['instructions']:
            for value in set(int(v,16) for v in re.findall(r'#([0-9A-F]{4})\b',item['operation'])):
                owners=[f for f in functions if f['region']==region['name'] and f['slot']==item['slot'] and f['offset']<=item['offset']<f['end_offset']]
                values[value].append(dict(address=item['address'],slot=item['slot'],offset=item['offset'],
                    operation=item['operation'],function_path=owners[0]['path'] if len(owners)==1 else None))
        by_region[region['name']]=(values,sorted(values))
    ranges=[]
    for resource in source_map:
        if resource['kind']!='unclassified':continue
        blob=(ROOT/resource['path']).read_bytes()
        assert len(blob)==resource['length'] and hashlib.sha256(blob).hexdigest()==resource['sha256']
        # Сверка физического ресурса с оригиналом, независимо от опубликованного SHA256 разметки.
        catalog=original[resource['slot']*16:(resource['slot']+1)*16]
        file_disk_offset=(catalog[15]*16+catalog[14])*256
        assert file_disk_offset==disk_entries[resource['slot']]['offset']
        assert 0<=resource['offset'] and resource['offset']+len(blob)<=catalog[13]*256
        disk_offset=file_disk_offset+resource['offset']
        assert blob==original[disk_offset:disk_offset+len(blob)]
        nonzero=[dict(file_offset=resource['offset']+index,value=value)
                 for index,value in enumerate(blob) if value]
        contexts=[];references=[]
        # Проверка только уже зарегистрированных переносов, параметр каталога не считается адресом загрузки.
        for region in flow:
            for block in region['blocks']:
                if block['slot']!=resource['slot']:continue
                first=max(resource['offset'],block['offset']);end=min(resource['offset']+resource['length'],block['offset']+block['length'])
                if first>=end:continue
                start_address=block['origin']+first-block['offset'];end_address=start_address+end-first
                contexts.append(dict(region=region['name'],file_offset=first,length=end-first,
                    start_address=start_address,end_exclusive=end_address,bank_context_not_added_by_this_check=True))
                consumers = [(region['name'], start_address, end_address)]
                fixed_start, fixed_end = max(start_address, 0x4000), min(end_address, 0xC000)
                if fixed_start < fixed_end:
                    consumers.extend((companion, fixed_start, fixed_end)
                                     for companion in FIXED_WINDOW_COMPANIONS.get(resource['slot'], ()))
                for name, low, high in consumers:
                    indexed,keys=by_region[name]
                    for literal in keys[bisect_left(keys,low):bisect_left(keys,high)]:
                        references.extend(dict(i,region=name,literal=literal,
                            candidate_target_offset=first+literal-start_address) for i in indexed[literal])
        ranges.append(dict(resource,runtime_contexts=contexts,candidate_literal_references=references,
            candidate_reference_count=len(references),semantic_purpose_proved=False,
            original_disk_offset=disk_offset,original_disk_bytes_matched=True,
            all_bytes_zero=not nonzero,nonzero_byte_count=len(nonzero),nonzero_file_bytes=nonzero))
    assert sum(r['length'] for r in ranges)==inventory['physical_bytes_by_kind']['unclassified']
    assert len(ranges)==inventory['ranges_by_kind']['unclassified']
    ranked=sorted(ranges,key=lambda r:(-bool(r['candidate_reference_count']),-r['candidate_reference_count'],-r['length'],r['slot'],r['offset']))
    result=dict(passed=True,method='physical_range_integrity_and_registered_region_and_fixed_window_literal_candidates',
        source_map_sha256=hashlib.sha256(source_map_bytes).hexdigest(),ranges=len(ranges),
        unclassified_bytes=sum(r['length'] for r in ranges),entries=ranked,
        literal_matches_are_not_memory_access_proof=True,cross_bank_reference_graph_complete=False,
        fixed_window_companions_checked=True,
        absence_of_candidates_does_not_prove_unused=True,source_map_changed=False,
        assembly_executed=False,native_execution=False)
    # Подсчёт заполнения сохраняет физические копии и не назначает им смысловой тип.
    zero_ranges=[row for row in ranges if row['all_bytes_zero']]
    nonzero_ranges=[row for row in ranges if not row['all_bytes_zero']]
    result['byte_contents']=dict(all_zero_ranges=len(zero_ranges),
        all_zero_range_bytes=sum(row['length'] for row in zero_ranges),
        ranges_containing_nonzero_bytes=len(nonzero_ranges),
        mixed_or_nonzero_range_bytes=sum(row['length'] for row in nonzero_ranges),
        nonzero_bytes=sum(row['nonzero_byte_count'] for row in nonzero_ranges),
        zero_bytes_in_nonzero_ranges=sum(row['length']-row['nonzero_byte_count'] for row in nonzero_ranges),
        original_disk_sha256=manifest['sha256'],original_disk_bytes_matched=True,
        zero_fill_does_not_prove_unused=True,semantic_classification_changed=False)
    result['object_table_alignment_classified'] = any(
        row.get('format') == 'ACTION_OBJECT_TABLE_ALIGNMENT' for row in source_map)
    add_literal_contexts(result)
    target=reports/'UnclassifiedRangeReferences.json';document=ROOT/'Docs/UnclassifiedRanges.md'
    after={target:(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'),
           document:document_text(result).encode('utf-8')}
    if args.check:
        assert json.loads(target.read_bytes()) == result, 'Реестр не совпадает с текущим исходным разбором'
        assert document.read_text('utf-8') == document_text(result), 'Документ не совпадает с реестром'
        print(json.dumps(dict(passed=True, ranges=len(ranges), bytes=result['unclassified_bytes'],
            unresolved_literal_candidates=result['unresolved_literal_candidates'],
            assembly_executed=False), indent=2))
        return
    if args.refresh:
        # Проверка ручных правок, разрешено обновить только документ, совпадающий с прежним реестром.
        before={p:p.read_bytes() for p in after}
        previous=json.loads(before[target]);assert before[document].decode('utf-8').replace('\r\n','\n')==document_text(previous)
        tag=hashlib.sha256(after[target]).hexdigest()[:16]
        candidate=ROOT/('Tools/Disasm/Research/Candidates/RangeReferences'+tag)
        history=ROOT/('Tools/Disasm/Research/History/BeforeRangeReferences'+tag)
        assert not candidate.exists() and not history.exists()
        for p,data in after.items():
            q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
        for p,data in before.items():assert p.read_bytes()==data
        for p,data in before.items():
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    else:
        assert all(not p.exists() for p in after)
    for path, data in after.items():
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='range-references-', suffix='.tmp', delete=False) as out:
            temporary = Path(out.name)
            out.write(data)
        try:
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
    print(json.dumps(dict(passed=True,ranges=len(ranges),bytes=result['unclassified_bytes'],
        top_candidates=[{k:r[k] for k in ('slot','offset','length','candidate_reference_count','path')} for r in ranked[:8]],
        semantic_classification_performed=False,assembly_executed=False),indent=2))


if __name__=='__main__':main()
