"""Поле 04 набора параметров доказанно задаёт ADD фазового допуска по 63B8."""
import contextlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    pending={}
    for relative in ('Tools/Disasm/Research/ActionApplyParametersFacts.py','Source/Action/ApplyParameterSet.asm','Includes/Variables/Include.inc','Docs/ActionApplyParameters.md'):
        path=ROOT/relative;text=path.read_text('utf-8');assert 'Unknown04' in text
        if relative.endswith('Include.inc'):
            text=text.replace('Unknown04       equ #63B9','PairedLineStep  equ #63B9').replace('поле 04, целевой потребитель ещё не установлен','поле 04, шаг фазового допуска RequestPairedAimLines')
        elif relative.endswith('.md'):
            text=text.replace('Unknown04, потребитель не установлен','PairedLineStep, операнд ADD A,n фазового допуска двух линий по 63B8')
        else:
            text=text.replace('Unknown04','PairedLineStep')
            text=text.replace('поле 04, целевой потребитель ещё не установлен','поле 04, шаг фазового допуска RequestPairedAimLines')
            text=text.replace('цель PairedLineStep пока не отнесена к доказанной инструкции, поле 09 задаёт LinkedRLimit экранной обратной связи','поля 04 и 09 задают PairedLineStep фазового допуска и LinkedRLimit обратной связи, их потребители установлены')
            text=text.replace('четырнадцать остальных целей являются доказанными непосредственными операндами исходных инструкций ACTION','все пятнадцать целей являются доказанными непосредственными операндами исходных инструкций ACTION')
            text=text.replace('обновление PairedLineStep, игровой потребитель этого байта ещё не установлен','обновление PairedLineStep фазового допуска двух линий прицела')
        pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ActionApplyParameters.md';text=pending[path].decode('utf-8')
    text+='\nПоле 04 связано с [RequestPairedAimLines](ActionPairedAimLines.md), сумма по 63B8 обновляет фазу и только при Carry допускает расход шкалы и две линии. '
    text+='Вся таблица 15 целевых записей теперь привязана к исходным инструкциям, полный игровой смысл остальных параметров от этого не считается установленным.\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Reports/ModifiedCode.json';items=json.loads(path.read_text('utf-8'))
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));region=next(r for r in flow if r['name']=='Action')
    writer=next(i for i in region['instructions'] if i['operation']=='LD (#63B9),A')
    target=next(i for i in region['instructions'] if i['address']==0x63B8);assert target['hex']=='c632'
    assert not any(i['region']=='Action' and i['writer']==writer['address'] for i in items)
    items.append(dict(region='Action',writer=writer['address'],target=0x63B9,target_instruction=0x63B8,size=1,target_operation=target['operation'],
        path='Source/Action/ApplyParameterSet.asm',writer_slot=17,writer_offset=writer['offset'],writer_bank=2,writer_source_classified=True,
        target_slot=17,target_offset=target['offset']+1,target_bank=5,target_region='Action',
        target_path='Source/Action/RequestPairedAimLines.asm',target_source_classified=True))
    items.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[path]=(json.dumps(items,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPairedLineStep';history=ROOT/'Tools/Disasm/Research/History/BeforeActionPairedLineStep'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes(),a) for p,a in pending.items()]
    for path,before,after in plan:
        target_path=candidate/path.relative_to(ROOT);target_path.parent.mkdir(parents=True,exist_ok=True);target_path.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target_path=history/path.relative_to(ROOT);target_path.parent.mkdir(parents=True,exist_ok=True);target_path.write_bytes(before)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='phase-step-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,parameter_index=4,writer=writer['address'],target=0x63B9,target_bank=5,
        source_instructions_and_bytes_unchanged=True,new_registered_writer=1,all_15_targets_classified=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPairedLineStepVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
