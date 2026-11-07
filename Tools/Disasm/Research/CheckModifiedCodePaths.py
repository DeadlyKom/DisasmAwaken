"""Связи реестра самомодификации с существующими файлами и физическими диапазонами."""
from pathlib import Path
import json
from CheckIntro import ROOT


def audit(records,source_map):
    errors=[];physical=0;path_only=0
    for item in records:
        for key in ('path','target_path'):
            if key not in item:continue
            path=ROOT/item[key]
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():
                errors.append(dict(region=item['region'],writer=item['writer'],kind='missing_or_outside_path',field=key,path=item[key]))
        if 'target_path' not in item:continue
        if not all(key in item for key in ('target_slot','target_offset')):
            path_only+=1
            continue
        physical+=1
        matches=[row for row in source_map if row['slot']==item['target_slot']
                 and row['offset']<=item['target_offset']
                 and item['target_offset']+item['size']<=row['offset']+row['length']]
        if len(matches)!=1 or matches[0]['path']!=item['target_path']:
            errors.append(dict(region=item['region'],writer=item['writer'],kind='wrong_target_range',
                path=item['target_path'],expected=[row['path'] for row in matches]))
    return dict(passed=not errors,records_checked=len(records),
                physical_target_ranges_checked=physical,target_paths_without_physical_context=path_only,
                all_records_have_physical_target_context=False,errors=errors,
                assembly_executed=False,native_execution=False)


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    records=json.loads((reports/'ModifiedCode.json').read_text('utf-8'))
    source_map=json.loads((reports/'SourceMap.json').read_text('utf-8'))
    result=audit(records,source_map)
    # Проверка чувствительности к ошибочному, но существующему пути внутри проекта, только в памяти.
    index=next(i for i,item in enumerate(records) if 'target_path' in item and 'target_offset' in item and 'target_slot' in item)
    probe=[dict(item) for item in records]
    probe[index]['target_path']='Source/Basic/ReadIntroSectors.asm'
    rejected=audit(probe,source_map)
    assert not rejected['passed'] and any(error['kind']=='wrong_target_range' for error in rejected['errors'])
    result['existing_but_wrong_target_path_probe_rejected']=True
    (reports/'ModifiedCodePathsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    assert result['passed']


if __name__=='__main__':main()
