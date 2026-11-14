"""Прямые вызовы пятнадцати потоков, контекст банка и физические байты.

Документация: ../../../Docs/ActionFoldedRandom.md#подтверждённые-прямые-потребители
"""
from collections import Counter
from hashlib import sha256
import json
import re

from CheckStationFlightCycle import ROOT,DISK,ENTRIES
from CheckActionParameterActivation import flat_action
from ActionRandomStreamLayout import STREAMS,DIRECT_USE_NOTES


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(DISK).hexdigest()==manifest['sha256']
    mapping=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_bytes())
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_bytes())
    flat=flat_action()
    roots={entry:index for index,entry,_ in STREAMS}
    calls={index:[] for index,_,_ in STREAMS}
    other=[]
    for group in flow:
        for row in group['instructions']:
            operation=re.sub(r'\s','',row['operation'])
            match=re.fullmatch(r'(CALL|JP)(?:(NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})',operation)
            if not match or int(match[3],16) not in roots:
                continue
            target=int(match[3],16)
            index=roots[target]
            entry=ENTRIES[row['slot']]
            raw=bytes.fromhex(row['hex'])
            assert len(raw)==3 and int.from_bytes(raw[1:],'little')==target
            offset=entry['offset']+row['offset']
            assert DISK[offset:offset+3]==raw
            # Разделение одноимённых числовых адресов других банков до назначения роли потока.
            if group['name'] not in ('Action','ActionBoot') or row['slot']!=17:
                other.append(dict(region=group['name'],slot=row['slot'],pc=row['address'],target=target))
                continue
            owners=[block for block in mapping if block['slot']==17 and block['kind']=='code'
                    and block['offset']<=row['offset']<block['offset']+block['length']]
            assert len(owners)==1
            owner=owners[0]
            details=[f for f in functions if f['path']==owner['path'] and f['region']==group['name']]
            assert details
            calls[index].append(dict(region=group['name'],pc=row['address'],file_offset=row['offset'],
                instruction=match[1],condition=match[2],original_hex=raw.hex(),source=owner['path'],
                caller_descriptions=sorted({f['description'] for f in details}),
                following_original_bytes_hex=DISK[offset+3:offset+19].hex()))
    accesses={index:[] for index,_,_ in STREAMS}
    for group in flow:
        if group['name'] not in ('Action','ActionBoot'):
            continue
        for row in group['instructions']:
            if row['slot']!=17:
                continue
            operation=re.sub(r'\s','',row['operation'])
            load=re.fullmatch(r'LD(HL|DE|BC|SP|IX|IY|A),\(#([0-9A-F]{4})\)',operation)
            store=re.fullmatch(r'LD\(#([0-9A-F]{4})\),(HL|DE|BC|SP|IX|IY|A)',operation)
            if not load and not store:
                continue
            address=int(load[2] if load else store[1],16)
            register=load[1] if load else store[2]
            width=1 if register=='A' else 2
            for index,_,pointer in STREAMS:
                touched=sorted(set(range(address,address+width)) & set(range(pointer,pointer+3)))
                if not touched:
                    continue
                raw=bytes.fromhex(row['hex']);offset=ENTRIES[17]['offset']+row['offset']
                assert DISK[offset:offset+len(raw)]==raw and int.from_bytes(raw[-2:],'little')==address
                owners=[b for b in mapping if b['slot']==17 and b['kind']=='code' and b['offset']<=row['offset']<b['offset']+b['length']]
                assert len(owners)==1
                accesses[index].append(dict(region=group['name'],pc=row['address'],operation=row['operation'],
                    kind='read' if load else 'write',address=address,width=width,source=owners[0]['path'],
                    original_hex=raw.hex(),field_offsets=[a-pointer for a in touched]))
    assert {r['source'] for r in accesses[3] if r['kind']=='read'}=={
        'Source/Action/SpawnAlternate.asm','Source/Action/FinishSpawnRecord.asm'}
    # Проверка совпадения числа прямых инструкций с опубликованными символическими исходниками.
    sources=Counter((index,row['source']) for index,rows in calls.items() for row in rows)
    for (index,path),count in sources.items():
        code='\n'.join(line.partition(';')[0] for line in (ROOT/path).read_text(encoding='utf-8').splitlines())
        named=re.findall(r'\b(?:CALL|JP)\s+(?:(?:NZ|Z|NC|C|PO|PE|P|M)\s*,\s*)?@Action\.NextRandomWord'+str(index)+r'\.Entry\b',code)
        assert len(named)==count,(index,path,count,len(named))
    for index,entry,pointer in STREAMS:
        assert bytes(flat[entry:entry+7])==bytes((0xD9,0x21,pointer&255,pointer>>8,0xC3,0x08,0xEC))
    assert not calls[6] and all(calls[index] for index in calls if index!=6)
    result=dict(passed=True,original_disk_sha256=manifest['sha256'],
        direct_instruction_count=sum(map(len,calls.values())),
        instruction_counts={str(index):len(rows) for index,rows in calls.items()},
        streams=[dict(index=index,entry=entry,state=pointer,local_use=DIRECT_USE_NOTES[index],
                      direct_callers=calls[index],direct_state_accesses=accesses[index]) for index,entry,pointer in STREAMS],
        other_bank_numeric_targets=other,current_source_call_counts_matched=True,
        all_original_wrapper_bytes_matched=True,computed_or_mutable_targets_excluded=False,
        all_reachable_gameplay_paths_proved=False,all_stream_roles_proved=False,
        probability_or_period_proved=False,execution_model_run=False,native_execution=False,assembly_executed=False)
    result=json.loads(json.dumps(result))
    path=ROOT/'Tools/Disasm/Reports/ActionRandomDirectCallersVerification.json'
    if path.exists():
        assert json.loads(path.read_bytes())==result
    else:
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('streams','other_bank_numeric_targets')},ensure_ascii=False))


if __name__=='__main__':
    main()
