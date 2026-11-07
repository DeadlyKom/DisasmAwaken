"""Физический контекст существующих явных целевых путей, без догадки о выбранном банке."""
import json
import os
from pathlib import Path
import tempfile
from CheckIntro import ROOT


def complete(records,source_map,flow):
    fixed=[]
    for item in records:
        if 'target_path' not in item or all(key in item for key in ('target_slot','target_offset')):continue
        rows=[row for row in source_map if row['path']==item['target_path']
              and row.get('origin') is not None and row['origin']<=item['target_instruction']
              and item['target']+item['size']<=row['origin']+row['length']]
        assert len(rows)==1 and rows[0]['kind']=='code',(item,rows)
        row=rows[0]
        region=item['target_path'].split('/')[1]
        assert item.get('target_region',region)==region
        target_region=next(value for value in flow if value['name']==region)
        instructions=[value for value in target_region['instructions']
                      if value['address']==item['target_instruction'] and value['slot']==row['slot']
                      and value['offset']==row['offset']+item['target_instruction']-row['origin']]
        assert len(instructions)==1 and instructions[0]['operation']==item['target_operation']
        instruction=instructions[0]
        assert item['target_instruction']<=item['target'] and item['target']+item['size']<=item['target_instruction']+len(bytes.fromhex(instruction['hex']))
        item.update(target_region=region,target_slot=row['slot'],
                    target_offset=row['offset']+item['target']-row['origin'],target_source_classified=True)
        fixed.append(dict(region=item['region'],writer=item['writer'],target_path=item['target_path'],
                          target_slot=item['target_slot'],target_offset=item['target_offset']))
    return fixed


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_text('utf-8'))
    records=read('ModifiedCode');source_map=read('SourceMap');flow=read('ControlFlow')
    previous=[dict(item) for item in records]
    fixed=complete(records,source_map,flow)
    assert len(fixed)==41
    # Проверка отсутствия изменения исходных полей, в том числе контекста банка и адресов инструкций.
    for before,after in zip(previous,records):
        assert all(after[key]==value for key,value in before.items())
    path=reports/'ModifiedCode.json'
    before=path.read_bytes();after=(json.dumps(records,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ExplicitMutationTargets/Tools/Disasm/Reports/ModifiedCode.json'
    history=ROOT/'Tools/Disasm/Research/History/BeforeExplicitMutationTargets/Tools/Disasm/Reports/ModifiedCode.json'
    assert not candidate.exists() and not history.exists()
    candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(after)
    assert path.read_bytes()==before
    history.parent.mkdir(parents=True,exist_ok=True);history.write_bytes(before)
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='mutation-targets-',suffix='.tmp',delete=False) as output:
        temporary=Path(output.name);output.write(after)
    try:os.replace(temporary,path)
    finally:
        if temporary.exists():temporary.unlink()
    (reports/'ExplicitMutationTargetCompletion.json').write_text(json.dumps(dict(
        passed=True,physical_context_added=fixed,bank_context_inferred=False,
        original_record_fields_preserved=True,assembly_executed=False),indent=2)+'\n',encoding='utf-8')
    print('Физический контекст дополнен у 41 явно связанной цели, банки и исходные поля не изменены')


if __name__=='__main__':main()
