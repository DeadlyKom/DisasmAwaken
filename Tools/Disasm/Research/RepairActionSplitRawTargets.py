"""Три адресные привязки E761 к оставшемуся бинарному диапазону после разделения F222."""
import json,os,tempfile
from CheckIntro import ROOT


def main():
    path=ROOT/'Tools/Disasm/Reports/ModifiedCode.json';before=path.read_bytes();items=json.loads(before)
    source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'));changed=[]
    for item in items:
        if item['region']!='Action' or item['writer'] not in (0xE77E,0xE787,0xE790):continue
        assert item['target_slot']==17 and item['target_bank']==0
        owner=next(p for p in source_map if p['slot']==17 and p['offset']<=item['target_offset']<p['offset']+p['length'])
        assert item['target'] in (0xF1ED,0xF1F0,0xF1FE) and owner['kind']=='unclassified'
        old=ROOT/item['target_path'];assert not old.exists() and (ROOT/owner['path']).is_file()
        changed.append(dict(writer=item['writer'],target=item['target'],before=item['target_path'],after=owner['path']))
        item.update(target_path=owner['path'],target_source_classified=False)
    assert len(changed)==3
    after=(json.dumps(items,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionSplitRawTargets/Tools/Disasm/Reports/ModifiedCode.json'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionSplitRawTargets/Tools/Disasm/Reports/ModifiedCode.json'
    assert not candidate.exists() and not history.exists()
    candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(after);assert path.read_bytes()==before
    history.parent.mkdir(parents=True,exist_ok=True);history.write_bytes(before)
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='targets-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write(after)
    os.replace(temporary,path)
    result=dict(passed=True,changed=changed,source_instructions_changed=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionSplitRawTargetsVerification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
