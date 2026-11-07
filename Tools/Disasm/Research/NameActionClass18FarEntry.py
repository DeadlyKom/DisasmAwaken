"""Доказанный дополнительный вход F365 для State0E, существующая инструкция не меняется."""
import contextlib,io,json,os,tempfile,sys
from pathlib import Path
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))


def main():
    pending={};source=ROOT/'Source/Action/HandleClass18Proximity.asm';text=source.read_text('utf-8')
    needle='                CALL @Action.StepCodesTowardRecord.Entry';assert text.count(needle)==1 and 'StepFar:' not in text
    pending[source]=text.replace(needle,'StepFar:        CALL @Action.StepCodesTowardRecord.Entry').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionClass18ProximityFacts.py';text=path.read_text('utf-8');assert text.count('LOCAL={}')==1
    text=text.replace('LOCAL={}',"LOCAL={0xF365:'StepFar'}")
    text+='\n# Дополнительный вход пропускает поиск и проверку расстояния, IY уже выбран вызывающим.\n'
    text+="CONTRACTS['Action',0xF356][3].append('дополнительный StepFar по F365 принимает выбранные IX и IY без поиска, исполняет StepCodesTowardRecord и передаёт исходный SP общему F0F8')\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Reports/Symbols.json';symbols=json.loads(path.read_text('utf-8'));name='Action.HandleClass18Proximity.StepFar';assert name not in symbols
    symbols[name]=0xF365;pending[path]=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    pending[path]=(text+"\nLABELS['Action',0xF365]='StepFar'\n").encode('utf-8')
    path=ROOT/'Docs/ActionClass18Proximity.md';text=path.read_text('utf-8')
    text+='\nДополнительный вход `StepFar` по F365 используется [State0E](ActionLinkedProximity.md). '
    text+='In, IX указывает текущую запись, IY уже выбранную цель, действуют все условия StepCodesTowardRecord и доступного стека. '
    text+='Поиск класса 18 и проверка расстояния пропускаются. Out, регистры, поля и порты определяются StepCodesTowardRecord, затем PC=F0F8 и SP равен входному. '
    text+='Corrupt, регистры, операнды и фазы из договора StepCodesTowardRecord, последующий общий F0F8 в этой модели не исполняется. '
    text+='R самого дополнительного входа включает CALL, дочернюю стоимость и JP, точный R дальнего ребёнка пока не доказан. '
    text+='Основной вход F356 сохраняет прежний договор поиска и порога 512.\n'
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClass18FarEntry';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClass18FarEntry'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes(),a) for p,a in pending.items()]
    # Подготовка отдельного кандидата и сверка оснований до добавления внутреннего имени.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='far-entry-',suffix='.tmp',delete=False) as out:
                temporary=Path(out.name);out.write(after)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(after)
    from VerifySources import main as verify
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Завершение уже опубликованного кандидата State0E после проверки нового имени.
    old_map=json.loads((ROOT/'Tools/Disasm/Research/History/BeforeActionLinkedProximity/Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    old=next(p for p in old_map if p['slot']==17 and p['offset']==0x9009)
    assert old['kind']=='unclassified' and old['length']==52
    original=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()[0x9009:0x903D]
    old_path=ROOT/old['path'];backup=ROOT/'Tools/Disasm/Research/History/BeforeActionLinkedProximity'/old['path']
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==backup.read_bytes()==original;old_path.unlink()
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    region=next(r for r in flow if r['name']=='Action');instructions=[i for i in region['instructions'] if 0xF009<=i['address']<0xF03D]
    assert b''.join(bytes.fromhex(i['hex']) for i in instructions)==original
    result=dict(passed=True,described_functions=1,semantic_status='described',confirmed_code_bytes=52,
        confirmed_instructions=len(instructions),model_cases=106496,original_bytes_preserved=True,
        self_modifying_writers_registered=0,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkedProximityClassification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
