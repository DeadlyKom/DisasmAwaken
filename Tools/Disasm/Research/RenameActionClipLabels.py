"""Смысловые имена 36 внутренних входов по побайтово проверенному соответствию двух графов."""
import contextlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckActionClipCasePaths import translated
from ClipCaseFacts import LABELS as PRIMARY
from MapClipCasesFacts import LABELS as PRIVATE
import ActionClipCasesFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionClipCasePathsVerification')['all_instruction_bytes_compared']
    assert read('ActionClipCaseRegistersVerification')['all_final_registers_except_R_proved']
    semantic={}
    for (region,address),name in {**PRIMARY,**PRIVATE}.items():
        if region=='Map':
            try:semantic[translated(address)]=name
            except AssertionError:pass
    assert set(facts.LOCAL)<=set(semantic)
    symbols=read('Symbols');functions=read('Functions');renames={};definitions={}
    for address,old in facts.LOCAL.items():
        new=semantic[address];assert new!=old and len(new)<=15
        owner=next(f for f in functions if f['region']=='Action' and f['address']<=address<f['address']+f['end_offset']-f['offset'])
        old_key='Action.'+owner['name']+'.'+old;new_key='Action.'+owner['name']+'.'+new
        assert symbols[old_key]==address and new_key not in symbols
        renames[old_key]=new_key;definitions.setdefault(owner['path'],[]).append((old,new))
    assert len(renames)==36
    pending={}
    # Изменение только подтверждённых ссылок и определений, чужие комментарии и форматирование сохраняются.
    for directory,patterns in (('Source',('*.asm','*.inc')),('Docs',('*.md',))):
        for pattern in patterns:
            for p in (ROOT/directory).rglob(pattern):
                before=p.read_text('utf-8');after=before
                for old,new in renames.items():after=after.replace(old,new)
                for old,new in definitions.get(p.relative_to(ROOT).as_posix(),()):
                    after,count=re.subn(r'^'+re.escape(old)+r':\s{1,}',(new+':').ljust(16),after,flags=re.M);assert count==1
                if before!=after:
                    lines=[]
                    for line in after.splitlines():
                        code,sep,note=line.partition(';')
                        if sep and code.strip():line=code.rstrip().ljust(80)+';'+note
                        lines.append(line)
                    pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
    for old,new in renames.items():symbols[new]=symbols.pop(old)
    pending[ROOT/'Tools/Disasm/Reports/Symbols.json']=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ActionClipCasesFacts.py';text=p.read_text('utf-8')
    for old,new in renames.items():text=text.replace(old,new)
    local={a:semantic[a] for a in facts.LOCAL}
    for key,value in (('LOCAL',local),('LABELS',{('Action',a):n for a,n in local.items()})):
        text,count=re.subn('^'+key+r'=.*$',key+'='+repr(value),text,flags=re.M);assert count==1
    pending[p]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClipInternalLabels';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClipInternalLabels'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes(),data) for p,data in pending.items()]
    for p,before,data in plan:
        c=candidate/p.relative_to(ROOT);c.parent.mkdir(parents=True,exist_ok=True);c.write_bytes(data)
    for p,before,data in plan:assert p.read_bytes()==before
    for p,before,data in plan:
        h=history/p.relative_to(ROOT);h.parent.mkdir(parents=True,exist_ok=True);h.write_bytes(before);p.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    report=dict(passed=True,renamed_internal_labels=len(renames),instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipInternalLabelsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
