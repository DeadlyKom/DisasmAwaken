"""Исправление ложного INC H по фактическому коду 00 14, с контрольными копиями."""
from pathlib import Path
import contextlib
import io
import json
import sys
from IntroScatterFacts import CONTRACTS

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from SourcePresentation import instructions


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=json.loads((ROOT/'Tools/Disasm/Reports/IntroScatterVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['patches_from_actual_phase_code']==[[0,0],[0,20]]
    pending={}
    for relative in ('Source/Intro/ScatterTextureToScreen.asm','Source/Intro/PresentInterlacedFrame.asm',
                     'Tools/Disasm/Research/IntroNotes.py','Tools/Disasm/Research/Contracts.py','Docs/Intro.md'):
        path=ROOT/relative;before=path.read_bytes();text=before.decode('utf-8').replace('\r\n','\n')
        text=text.replace('INC H NOP','NOP INC D')
        text=text.replace('меняется половина таблицы источников','меняется страница приёмника, таблица источников сохраняется')
        text=text.replace('соседняя страница источников выбирается инструкцией INC H',
                          'соседняя страница приёмника выбирается инструкцией INC D')
        text=text.replace('фаза равна #80 и добавление к H не требуется',
                          'фаза равна #80 и коррекция страницы приёмника не требуется')
        if relative=='Source/Intro/ScatterTextureToScreen.asm':
            start=text.index('; In:');end=text.index('; -----------------------------------------',start)
            header=[]
            for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['Intro',0x6827]):
                header+=['                ; '+heading+':']+['                ;   '+v for v in values]
            text=text[:start]+'\n'.join(header)+'\n                '+text[end:]
        if relative.startswith('Source/'):
            text=text.replace('; Документация [Intro](../../Docs/FunctionDetails/Intro.md)',
                '; Документация [Intro](../../Docs/FunctionDetails/Intro.md)\n                ; Документация [экранный перенос](../../Docs/IntroScatter.md)')
            assert instructions(before.decode('utf-8'))==instructions(text)
            lines=[]
            for line in text.splitlines():
                code,sep,note=line.partition(';')
                if sep and code.strip():
                    assert len(code.rstrip())<80
                    line=code.rstrip().ljust(80)+';'+note
                lines.append(line)
            text='\n'.join(lines)+'\n'
        if relative.endswith('Contracts.py'):
            assert 'from IntroScatterFacts import' not in text
            text+='\nfrom IntroScatterFacts import CONTRACTS as INTRO_SCATTER_CONTRACTS\nCONTRACTS.update(INTRO_SCATTER_CONTRACTS)\n'
        if relative=='Docs/Intro.md':
            text+='\nВставка `00 14` получена настоящим выбором фазы и проверена как `NOP / INC D`.\nПодробный контракт, исправление прежней трактовки и границы проверки описаны\nв [экранном переносе](IntroScatter.md).\n'
        pending[relative]=(before,text.encode('utf-8'))
    relative='Tools/Disasm/Research/SemanticNames.py'
    before=(ROOT/relative).read_bytes()
    text=before.decode('utf-8')+'\nDOCUMENTS["Intro", 0x6827] = ("IntroScatter", "экранный перенос")\nDOCUMENTS["Intro", 0x67F1] = ("IntroScatter", "экранный перенос")\n'
    pending[relative]=(before,text.encode('utf-8'))
    candidate=ROOT/'Tools/Disasm/Research/Candidates/IntroScatter'
    history=ROOT/'Tools/Disasm/Research/History/BeforeIntroScatter'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и сохранение исходного состояния.
    for relative,(before,after) in pending.items():
        for folder,data in ((candidate,after),(history,before)):
            path=folder/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    # Проверка отсутствия посторонних изменений перед публикацией.
    for relative,(before,_) in pending.items():assert (ROOT/relative).read_bytes()==before,relative
    for relative,(_,after) in pending.items():(ROOT/relative).write_bytes(after)
    verify()
    report=dict(passed=True,changed_files=list(pending),instruction_bytes_unchanged=True,
        old_source_page_interpretation_rejected=True,actual_patch=[0,20],
        model_cases=proof['total_cases'],assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroScatterClassification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
