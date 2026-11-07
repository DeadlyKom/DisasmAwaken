"""Охват настоящих целей таблицы EF50, отдельно от числа уже оформленных функций."""
import json
from CheckIntro import ROOT


def audit():
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_text('utf-8'))
    functions,source_map=read('Functions'),read('SourceMap')
    raw=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    rows=[]
    for state in range(22):
        target=int.from_bytes(raw[0x8F50+2*state:0x8F52+2*state],'little')
        # Проверка физического диапазона цели в исходном верхнем окне ACTION банка 0.
        matches=[row for row in source_map if row['slot']==17
                 and row['offset']<=target-0x6000<row['offset']+row['length']]
        assert len(matches)==1
        owners=[function for function in functions if function['region']=='Action' and function['address']==target]
        assert len(owners)<=1
        rows.append(dict(state=state,target=target,registered=bool(owners),
            function=owners[0]['name'] if owners else None,
            physical_path=matches[0]['path'],physical_kind=matches[0]['kind']))
    pending=[row for row in rows if not row['registered']]
    return dict(passed=True,table_entries=22,registered_entries=22-len(pending),
                unregistered_entries=len(pending),unregistered_targets=pending,
                all_state_handlers_registered=not pending,all_state_algorithms_proved=False,
                original_table_targets_proved=True,native_calls_to_all_states_proved=False,
                rows=rows,assembly_executed=False,native_execution=False)


if __name__=='__main__':
    result=audit()
    (ROOT/'Tools/Disasm/Reports/ObjectStateCoverage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key not in ('rows','unregistered_targets')},indent=2))
