"""Шесть адресных переходов к уже доказанным целям, неизвестные динамические цели не переименовываются."""
import contextlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';symbols=json.loads((reports/'Symbols.json').read_bytes())
    mappings={('D3D',0xEC28):{0xEEEE:'D3D.RestorePreviewStack.Entry'},('D3D',0xEE24):{0xEEEE:'D3D.RestorePreviewStack.Entry'},
      ('Voxel',0xF9E9):{0xF9F9:'Voxel.ProjectEffectPoint.ShiftVertical',0xFA1C:'Voxel.ProjectEffectPoint.ShiftHorizontal'}}
    for targets in mappings.values():
        for address,name in targets.items():assert symbols[name]==address
    functions=json.loads((reports/'Functions.json').read_bytes());pending={};changed=0;sites=[]
    for (region,address),targets in mappings.items():
        function=next(f for f in functions if f['region']==region and f['address']==address);path=ROOT/function['path'];text=path.read_text('utf-8');local=0
        lines=[]
        for number,line in enumerate(text.splitlines(),1):
            code,sep,comment=line.partition(';');count=0
            for target,name in targets.items():
                needle='#'+format(target,'04X')
                if needle in code and any(op in code for op in ('JP ','JR ')):
                    code=code.replace(needle,'@'+name);count+=1;sites.append(dict(path=function['path'],line=number,target=target,name=name))
            if count:line=code.rstrip().ljust(80)+';'+comment if sep else code.rstrip();local+=count
            lines.append(line)
        assert local==(3 if address==0xEE24 else 2 if region=='Voxel' else 1)
        changed+=local;pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    assert changed==6,changed
    helper='"""Только шесть переходов к существующим доказанным меткам."""\nTARGETS='+repr(mappings)+'\n\n'
    helper+='def name_operands(region,function_address,operation):\n    if not operation.startswith(("JP ","JR ")):return operation\n    for address,name in TARGETS.get((region,function_address),{}).items():operation=operation.replace("#"+format(address,"04X"),"@"+name)\n    return operation\n'
    pending[ROOT/'Tools/Disasm/Research/ConfirmedControlTargetNames.py']=helper.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='def name_operands(region, function_address, operation):';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = confirmed_control_target_name_operands(region,function_address,operation)')
    text+='\nfrom ConfirmedControlTargetNames import name_operands as confirmed_control_target_name_operands\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ConfirmedControlTargets';history=ROOT/'Tools/Disasm/Research/History/BeforeConfirmedControlTargets';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,renamed_targets=changed,sites=sites,existing_proved_symbol_values_checked=True,
        unknown_dynamic_targets_unchanged=True,original_instructions_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ConfirmedControlTargetNamesVerification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='sites'},indent=2))


if __name__=='__main__':main()
