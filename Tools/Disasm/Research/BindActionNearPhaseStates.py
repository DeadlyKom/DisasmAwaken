"""Связь двух доказанных состояний и фиксация жёсткого порядка физического продолжения."""
from pathlib import Path
import contextlib,importlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))


def verify_and_record():
    with contextlib.redirect_stdout(io.StringIO()):
        import ActionObjectStateHandlersData
        importlib.reload(ActionObjectStateHandlersData)
        import VerifySources
        importlib.reload(VerifySources).main()
    result=dict(passed=True,new_state_bindings=2,physical_pointer_words_preserved=True,
        include_order_explicit=True,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearPhaseBindingsClassification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    proof=json.loads((reports/'ActionNearPhaseVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==75008
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionNearPhaseBindings'
    if candidate.exists():
        # Проверка прерванного завершения, уже опубликованные файлы должны совпадать с отдельным кандидатом.
        for relative in ('Tools/Disasm/Research/ActionObjectStateHandlersData.py','Source/Action/Data/ObjectStateHandlers.asm','Source/Files/17_ACTION.inc'):
            assert (ROOT/relative).read_bytes()==(candidate/relative).read_bytes()
        verify_and_record();return
    pending={};path=ROOT/'Tools/Disasm/Research/ActionObjectStateHandlersData.py';text=path.read_text('utf-8')
    marker='KNOWN_HANDLERS = {';assert text.count(marker)==1
    bindings={0xF07C:'Action.UpdatePhaseAndNearVector.Entry',0xF081:'Action.UpdateLinkedOrNearPhase.Entry'}
    for address,name in bindings.items():assert hex(address).upper().replace('0X','0x') not in text
    additions=''.join(f"0x{address:04X}: {name!r},\n                  " for address,name in bindings.items())
    pending[path]=text.replace(marker,marker+additions).encode('utf-8')
    path=ROOT/'Source/Action/Data/ObjectStateHandlers.asm';text=path.read_text('utf-8')
    for address,name in bindings.items():
        old='#'+format(address,'04X');assert text.count(old)==1
        lines=[]
        for line in text.splitlines():
            if old in line:
                code,separator,note=line.partition(';');assert code.strip()==old and separator
                line=code.replace(old,'@'+name).rstrip().ljust(80)+';'+note
            lines.append(line)
        text='\n'.join(lines)+'\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    for number,name in enumerate(('UpdateLinkedOrNearPhase','UpdateNearVectorPhase')):
        needle='                include "../Action/'+name+'.asm"';assert text.count(needle)==1
        text=text.replace(needle,needle.ljust(80)+'; ('+str(number)+') жёсткий порядок, продолжение после невыполненного JP C')
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionNearPhaseBindings'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionNearPhaseBindings'
    assert not candidate.exists() and not history.exists()
    plan=[(path,path.read_bytes(),data) for path,data in pending.items()]
    # Подготовка отдельного кандидата и сравнение оснований, таблица сохраняет два исходных слова.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        path.write_bytes(after)
    # Перезагрузка проверки после обновления экспортных привязок, сборка не запускается.
    verify_and_record()


if __name__=='__main__':main()
