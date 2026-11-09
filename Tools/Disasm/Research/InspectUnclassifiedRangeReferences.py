"""Приоритеты оставшихся физических диапазонов, числовое совпадение не является доказательством обращения."""
from bisect import bisect_left
from collections import defaultdict
import argparse,hashlib,json,os,re,tempfile
from pathlib import Path
from CheckIntro import ROOT


def document_text(result):
    lines=['# Оставшиеся физические диапазоны','',
        'Это список текущих неизвестных, не результат их смысловой классификации. Числовое совпадение внутри той же зарегистрированной области даёт только кандидата обращения. Константа может не быть адресом, возможны другие банки и косвенные обращения. Отсутствие кандидатов не означает неиспользуемость.','',
        '[Проверка](../Tools/Disasm/Research/InspectUnclassifiedRangeReferences.py), [полный реестр кандидатов](../Tools/Disasm/Reports/UnclassifiedRangeReferences.json). Адресные контексты взяты из зарегистрированных блоков переноса, параметр каталога не используется вместо пути загрузки.','',
        f"Число диапазонов {result['ranges']}, объём {result['unclassified_bytes']} байт. Список привязан к SHA256 SourceMap `{result['source_map_sha256']}` и требует пересчёта после изменения разметки.",'',
        '| Слот | Смещение файла | Байтов | Числовых кандидатов | Ресурс |','|---|---|---|---|---|']
    for row in result['entries']:
        path=row['path'];lines.append(f"| {row['slot']} | {row['offset']:04X} | {row['length']} | {row['candidate_reference_count']} | [{path.rsplit('/',1)[-1]}](../{path}) |")
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    reports=ROOT/'Tools/Disasm/Reports'
    source_map_bytes=(reports/'SourceMap.json').read_bytes();source_map=json.loads(source_map_bytes)
    inventory=json.loads((reports/'Inventory.json').read_text('utf-8'))
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
                indexed,keys=by_region[region['name']]
                for literal in keys[bisect_left(keys,start_address):bisect_left(keys,end_address)]:
                    references.extend(dict(i,region=region['name'],literal=literal,
                        candidate_target_offset=first+literal-start_address) for i in indexed[literal])
        ranges.append(dict(resource,runtime_contexts=contexts,candidate_literal_references=references,
            candidate_reference_count=len(references),semantic_purpose_proved=False))
    assert sum(r['length'] for r in ranges)==inventory['physical_bytes_by_kind']['unclassified']
    assert len(ranges)==inventory['ranges_by_kind']['unclassified']
    ranked=sorted(ranges,key=lambda r:(-bool(r['candidate_reference_count']),-r['candidate_reference_count'],-r['length'],r['slot'],r['offset']))
    result=dict(passed=True,method='physical_range_integrity_and_same_registered_region_literal_candidates',
        source_map_sha256=hashlib.sha256(source_map_bytes).hexdigest(),ranges=len(ranges),
        unclassified_bytes=sum(r['length'] for r in ranges),entries=ranked,
        literal_matches_are_not_memory_access_proof=True,cross_bank_reference_graph_complete=False,
        absence_of_candidates_does_not_prove_unused=True,source_map_changed=False,
        assembly_executed=False,native_execution=False)
    target=reports/'UnclassifiedRangeReferences.json';document=ROOT/'Docs/UnclassifiedRanges.md'
    after={target:(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'),
           document:document_text(result).encode('utf-8')}
    if args.refresh:
        # Проверка ручных правок, разрешено обновить только документ, совпадающий с прежним реестром.
        before={p:p.read_bytes() for p in after}
        previous=json.loads(before[target]);assert before[document].decode('utf-8').replace('\r\n','\n')==document_text(previous)
        tag=result['source_map_sha256'][:16]
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
