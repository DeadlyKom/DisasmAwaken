"""Охват 26 физических классов и 11 различных целей таблицы 64F0 перенесённого ACTION."""
import json
from CheckIntro import ROOT


def audit():
    reports=ROOT/'Tools/Disasm/Reports'
    functions=json.loads((reports/'Functions.json').read_text('utf-8'))
    source_map=json.loads((reports/'SourceMap.json').read_text('utf-8'))
    raw=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();rows=[]
    for code in range(26):
        target=int.from_bytes(raw[0x72D+2*code:0x72F+2*code],'little')
        offset=target-0x6000+0x23D
        physical=[row for row in source_map if row['slot']==17 and row['offset']<=offset<row['offset']+row['length']]
        assert len(physical)==1
        owners=[function for function in functions if function['region']=='Action' and function['address']==target]
        assert len(owners)<=1
        rows.append(dict(class_code=code,target=target,registered=bool(owners),
            function=owners[0]['name'] if owners else None,physical_path=physical[0]['path'],physical_kind=physical[0]['kind']))
    pending=[row for row in rows if not row['registered']]
    return dict(passed=True,table_entries=26,unique_targets=len({row['target'] for row in rows}),
        registered_entries=26-len(pending),unregistered_entries=len(pending),unregistered_targets=pending,
        all_class_targets_registered=not pending,game_roles_of_all_class_codes_proved=False,
        full_state_dispatch_chains_proved=False,rows=rows,assembly_executed=False,native_execution=False)


if __name__=='__main__':
    result=audit()
    (ROOT/'Tools/Disasm/Reports/ClassHandlerCoverage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key not in ('rows','unregistered_targets')},indent=2))
