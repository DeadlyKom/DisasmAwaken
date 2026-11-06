"""Точечная публикация проверенного контракта с сохранением тела и ручных комментариев."""
from pathlib import Path
import contextlib
import io
import json
import sys
from IntroAttributeWriterFacts import CONTRACTS

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from SourcePresentation import instructions


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=json.loads((ROOT/'Tools/Disasm/Reports/IntroAttributeWriterVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==1536
    pending={}

    def update(relative,after):
        path=ROOT/relative
        before=path.read_bytes() if path.exists() else None
        pending[relative]=(before,after.encode('utf-8'))

    relative='Source/Intro/BuildAttributeWriter.asm'
    original=(ROOT/relative).read_text('utf-8')
    assert ';   Unknown, регистровый контракт ещё не доказан' in original
    start=original.index('; In:')
    end=original.index('; -----------------------------------------',start)
    header=[]
    for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['Intro',0x692D]):
        header+=['                ; '+heading+':']+['                ;   '+value for value in values]
    after=original[:start]+'\n'.join(header)+'\n                '+original[end:]
    after=after.replace('; Документация [Intro](../../Docs/FunctionDetails/Intro.md)',
        '; Документация [Intro](../../Docs/FunctionDetails/Intro.md)\n                ; Документация [писатель атрибутов](../../Docs/IntroAttributeWriter.md)')
    assert instructions(original)==instructions(after)
    update(relative,after)
    relative='Tools/Disasm/Research/Contracts.py'
    text=(ROOT/relative).read_text('utf-8')
    assert 'from IntroAttributeWriterFacts import' not in text
    update(relative,text+'\nfrom IntroAttributeWriterFacts import CONTRACTS as INTRO_ATTRIBUTE_WRITER_CONTRACTS\nCONTRACTS.update(INTRO_ATTRIBUTE_WRITER_CONTRACTS)\n')
    relative='Tools/Disasm/Research/SemanticNames.py'
    text=(ROOT/relative).read_text('utf-8')
    update(relative,text+'\nDOCUMENTS["Intro", 0x692D] = ("IntroAttributeWriter", "писатель атрибутов")\n')
    relative='Docs/FunctionDetails/Intro.md'
    text=(ROOT/relative).read_text('utf-8')
    anchor='[Intro.BuildAttributeWriter](../../Source/Intro/BuildAttributeWriter.asm)'
    assert text.count(anchor)==1
    update(relative,text.replace(anchor,anchor+'\n\n[Полный контракт и проверка](../IntroAttributeWriter.md).'))
    relative='Docs/Intro.md'
    text=(ROOT/relative).read_text('utf-8')
    update(relative,text+'\nПодробный контракт полного построителя, включая обе разные матрицы и альтернативные регистры, описан в [писателе атрибутов](IntroAttributeWriter.md).\n')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/IntroAttributeWriter'
    history=ROOT/'Tools/Disasm/Research/History/BeforeIntroAttributeWriter'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и контрольной копии до замены исходников.
    for relative,(before,after) in pending.items():
        path=candidate/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
        if before is not None:
            path=history/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(before)
    # Проверка отсутствия конкурирующих изменений после подготовки кандидата.
    for relative,(before,after) in pending.items():
        path=ROOT/relative
        assert (path.read_bytes() if path.exists() else None)==before,relative
    for relative,(_,after) in pending.items():(ROOT/relative).write_bytes(after)
    verify()
    report=dict(passed=True,changed_files=list(pending),instructions_unchanged=True,
        full_allocation_bytes_verified=True,model_cases=proof['total_cases'],assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroAttributeWriterClassification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
