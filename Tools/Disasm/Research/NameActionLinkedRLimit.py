"""Доказанный параметр 09, операнд CP по E823 и его писатель AC8E."""
import contextlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    pending={};before_note='две цели Unknown04 и Unknown09 пока не отнесены к доказанным инструкциям или полям данных'
    after_note='цель Unknown04 пока не отнесена к доказанной инструкции, поле 09 задаёт LinkedRLimit экранной обратной связи'
    for relative in ('Tools/Disasm/Research/ActionApplyParametersFacts.py','Source/Action/ApplyParameterSet.asm','Includes/Variables/Include.inc','Docs/ActionApplyParameters.md'):
        path=ROOT/relative;text=path.read_text('utf-8');assert 'Unknown09' in text
        if relative.endswith('Include.inc'):
            old='Unknown09       equ #E823';assert text.count(old)==1
            text=text.replace(old,'LinkedRLimit    equ #E823').replace('поле 09, целевой потребитель верхнего банка 0 ещё не установлен','поле 09, порог R обратной связи в CheckAndToggleLinkedOverlay')
        elif relative.endswith('.md'):
            text=text.replace('Unknown09, потребитель банка 0 не установлен','LinkedRLimit, операнд CP R по E822, запись обратной связи при R не меньше порога')
        else:
            text=text.replace('Unknown09','LinkedRLimit').replace(before_note.replace('Unknown09','LinkedRLimit'),after_note)
            text=text.replace('поле 09, целевой потребитель верхнего банка 0 ещё не установлен','поле 09, порог R обратной связи в CheckAndToggleLinkedOverlay')
            text=text.replace('тринадцать остальных целей являются доказанными непосредственными операндами исходных инструкций ACTION','четырнадцать остальных целей являются доказанными непосредственными операндами исходных инструкций ACTION')
            text=text.replace('обновление LinkedRLimit в выбранном верхнем банке 0','обновление порога R обратной связи CheckAndToggleLinkedOverlay в банке 0')
        pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ActionApplyParameters.md';text=pending[path].decode('utf-8')
    text+='\nПоле 09 установлено по [CheckAndToggleLinkedOverlay](ActionLinkedOverlay.md), адрес E823 является непосредственным операндом CP по E822. '
    text+='Писатель AC8E регистрируется в физическом банке 2, цель в верхнем банке 0. Порог влияет на запись бита 0 LinkFlags и обратного LinkedIndex до проверок знаков и переполнений.\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Reports/ModifiedCode.json';items=json.loads(path.read_text('utf-8'))
    assert not any(i['region']=='Action' and i['writer']==0xAC8E for i in items)
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));region=next(r for r in flow if r['name']=='Action')
    writer=next(i for i in region['instructions'] if i['address']==0xAC8E);target=next(i for i in region['instructions'] if i['address']==0xE822)
    assert writer['hex']=='3223e8' and target['hex']=='fe4a'
    items.append(dict(region='Action',writer=0xAC8E,target=0xE823,target_instruction=0xE822,size=1,target_operation=target['operation'],
        path='Source/Action/ApplyParameterSet.asm',writer_slot=17,writer_offset=writer['offset'],writer_bank=2,writer_source_classified=True,
        target_slot=17,target_offset=target['offset']+1,target_bank=0,target_region='Action',target_path='Source/Action/CheckAndToggleLinkedOverlay.asm',target_source_classified=True))
    items.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[path]=(json.dumps(items,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionLinkedRLimit';history=ROOT/'Tools/Disasm/Research/History/BeforeActionLinkedRLimit'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes(),a) for p,a in pending.items()]
    for path,before,after in plan:
        target_path=candidate/path.relative_to(ROOT);target_path.parent.mkdir(parents=True,exist_ok=True);target_path.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target_path=history/path.relative_to(ROOT);target_path.parent.mkdir(parents=True,exist_ok=True);target_path.write_bytes(before)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='linked-r-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,parameter_index=9,writer=0xAC8E,target=0xE823,target_bank=0,source_instructions_and_bytes_unchanged=True,new_registered_writer=1,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedRLimitVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
