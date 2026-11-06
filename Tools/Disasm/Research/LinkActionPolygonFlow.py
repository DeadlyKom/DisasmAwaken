"""Связывание двенадцати уже проверенных фрагментов без смены инструкций и размещения."""
import contextlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from ActionPolygonFlowNames import TARGETS,name_operands


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    symbols=read('Symbols');functions=read('Functions')
    for address,name in TARGETS.items():assert symbols[name]==address
    selected=[f for f in functions if f['region']=='Action' and 0xD1C0<=f['address']<0xD5C9]
    assert len(selected)==12 and sum(f['end_offset']-f['offset'] for f in selected)==1033
    pending={};changes=0
    # Замена только числовых целей инструкций, комментарии и физические поля сохраняются.
    for function in selected:
        path=ROOT/function['path'];lines=[]
        for line in path.read_text('utf-8').splitlines():
            code,sep,note=line.partition(';')
            if code.strip():
                before=code[16:].strip();after=name_operands('Action',function['address'],before)
                if before!=after:
                    changes+=1;code=code[:16]+after
                    line=code.rstrip().ljust(80)+';'+note if sep else code.rstrip()
            lines.append(line)
        data=('\n'.join(lines)+'\n').encode('utf-8')
        if data!=path.read_bytes():pending[path]=data
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle)==1 and 'from ActionPolygonFlowNames import' not in text
    text=text.replace(needle,needle+'\n    operation = action_polygon_flow_names(region, function_address, operation)')
    text+='\nfrom ActionPolygonFlowNames import name_operands as action_polygon_flow_names\n'
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPolygonFlowNames'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionPolygonFlowNames'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes(),data) for p,data in pending.items()]
    for p,before,data in plan:
        target=candidate/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for p,before,data in plan:assert p.read_bytes()==before
    for p,before,data in plan:
        target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before);p.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,functions=12,code_bytes=1033,renamed_numeric_targets=changes,
        instructions_changed=0,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonFlowNamesVerification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
