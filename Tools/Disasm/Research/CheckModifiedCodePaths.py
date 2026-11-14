"""Связи реестра самомодификации с существующими файлами и физическими диапазонами."""
from pathlib import Path
import json,re
from CheckIntro import ROOT


def audit_document(records,text):
    """Соответствие строк документа текущему реестру, поясняющие разделы не перезаписываются."""
    pattern=r'\| (\w+) \| #([0-9A-F]{4}) \| #([0-9A-F]{4}) \| `([^`]+)` \| \[([^]]+)\]\(\.\./([^)]+)\) \|'
    actual=[]
    for line in text.splitlines():
        match=re.fullmatch(pattern,line)
        if match:
            actual.append((match[1],int(match[2],16),int(match[3],16),match[4],match[5],match[6]))
    expected=[(item['region'],item['writer'],item['target'],item['target_operation'],
               Path(item['path']).name,item['path']) for item in records]
    return dict(passed=actual==expected,document_rows=len(actual),registry_records=len(expected),
                order_operations_link_labels_and_writer_paths_checked=True)


def audit(records,source_map):
    errors=[];physical=0;path_only=0
    reports=ROOT/'Tools/Disasm/Reports'
    functions=json.loads((reports/'Functions.json').read_bytes())
    flow=json.loads((reports/'ControlFlow.json').read_bytes())
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entries={entry['slot']:entry for entry in manifest['entries']}
    disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    instructions={}
    for region in flow:
        for instruction in region['instructions']:
            instructions.setdefault((region['name'],instruction['address']),[]).append(instruction)
    writer_instructions=set()
    for item in records:
        for key in ('path','target_path'):
            if key not in item:continue
            path=ROOT/item[key]
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():
                errors.append(dict(region=item['region'],writer=item['writer'],kind='missing_or_outside_path',field=key,path=item[key]))
        # Проверка принадлежности писателя текущей процедуре и его исходных дисковых байтов.
        writers=instructions.get((item['region'],item['writer']),[])
        owners=[function for function in functions if function['region']==item['region']
                and function['address']<=item['writer']<function['address']+function['end_offset']-function['offset']]
        if len(owners)!=1 or owners[0]['path']!=item['path']:
            errors.append(dict(region=item['region'],writer=item['writer'],kind='wrong_writer_source',
                path=item['path'],expected=[function['path'] for function in owners]))
        if len(writers)!=1:
            errors.append(dict(region=item['region'],writer=item['writer'],kind='ambiguous_writer_instruction',matches=len(writers)))
        else:
            instruction=writers[0];entry=entries[instruction['slot']]
            raw=bytes.fromhex(instruction['hex']);offset=instruction['offset']
            start=entry['offset']+offset
            if not (0<=offset and offset+len(raw)<=entry['allocated_length'] and disk[start:start+len(raw)]==raw):
                errors.append(dict(region=item['region'],writer=item['writer'],kind='writer_bytes_differ_from_original'))
            writer_instructions.add((item['region'],item['writer']))
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
                writer_source_ranges_checked=len(records),unique_writer_instructions_checked=len(writer_instructions),
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
    # Проверка чувствительности к существующему, но неверному файлу писателя, только в памяти.
    writer_probe=[dict(item) for item in records]
    writer_probe[index]['path']='Source/Basic/ReadIntroSectors.asm'
    rejected_writer=audit(writer_probe,source_map)
    assert not rejected_writer['passed'] and any(error['kind']=='wrong_writer_source' for error in rejected_writer['errors'])
    result['existing_but_wrong_writer_path_probe_rejected']=True
    # Проверка таблицы документа и чувствительности к подмене существующей ссылки.
    text=(ROOT/'Docs/ModifiedCode.md').read_text('utf-8')
    document=audit_document(records,text)
    assert document['passed'],document
    original_link=f"(../{records[0]['path']})"
    assert original_link in text
    changed=text.replace(original_link,'(../Source/Basic/ReadIntroSectors.asm)',1)
    assert not audit_document(records,changed)['passed']
    result['document_verification']=document
    result['wrong_document_writer_link_probe_rejected']=True
    (reports/'ModifiedCodePathsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    assert result['passed']


if __name__=='__main__':main()
