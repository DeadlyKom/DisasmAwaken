"""Кандидат точечного уточнения счётчиков с защитой исходных инструкций."""
from pathlib import Path
import contextlib
import io
import json
import re
import sys
from IntroTextureScaleFacts import CONTRACTS,LABELS,FIELDS,name_operands

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=json.loads((ROOT/'Tools/Disasm/Reports/IntroTextureScaleVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==10256
    pending={}

    def update(relative,after):
        path=ROOT/relative
        pending[relative]=(path.read_bytes(),after.encode('utf-8'))

    symbols_path='Tools/Disasm/Reports/Symbols.json'
    symbols=json.loads((ROOT/symbols_path).read_text('utf-8'))
    renames={}
    for (_,address),name in LABELS.items():
        before='Intro.AdvanceTextureScale.Point'+format(address,'04X')
        after='Intro.AdvanceTextureScale.'+name
        assert symbols[before]==address and after not in symbols
        symbols[after]=symbols.pop(before);renames[before]=after
    update(symbols_path,json.dumps(symbols,ensure_ascii=False,indent=2)+'\n')
    relative='Source/Intro/AdvanceTextureScale.asm'
    text=(ROOT/relative).read_text('utf-8')
    assert ';   Unknown, регистровый контракт ещё не доказан' in text
    start=text.index('; In:');end=text.index('; -----------------------------------------',start)
    header=[]
    for heading,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['Intro',0x6C21]):
        header+=['                ; '+heading+':']+['                ;   '+v for v in values]
    text=text[:start]+'\n'.join(header)+'\n                '+text[end:]
    text=text.replace('; Документация [Intro](../../Docs/FunctionDetails/Intro.md)',
        '; Документация [Intro](../../Docs/FunctionDetails/Intro.md)\n                ; Документация [масштаб текстуры](../../Docs/IntroTextureScale.md)')
    for before,after in renames.items():
        text=text.replace(before,after)
        text=re.sub(r'^'+before.rsplit('.',1)[1]+r':\s*',
                    (after.rsplit('.',1)[1]+':').ljust(16),text,flags=re.M)
    lines=[]
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith(';'):
            code,sep,note=line.partition(';')
            code=code[:16]+name_operands('Intro',0x6C21,code[16:])
            if sep:
                assert len(code.rstrip())<80
                line=code.rstrip().ljust(80)+';'+note
            else:line=code
        lines.append(line)
    update(relative,'\n'.join(lines)+'\n')
    relative='Source/Intro/SelectTexturePointerRow.asm'
    text=(ROOT/relative).read_text('utf-8')
    update(relative,text.replace('(#6BB2)','(@IntroScaleState.PointerRow)'))
    relative='Includes/Variables/Include.inc'
    text=(ROOT/relative).read_text('utf-8')
    assert 'module IntroScaleState' not in text
    block='\n                ; Операнды исходного кода, новая память не выделяется\n                module IntroScaleState\n'
    for name,value,note in FIELDS:
        block+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    block+='                endmodule\n\n'
    assert text.count('                endif')==1
    update(relative,text.replace('                endif',block+'                endif'))
    relative='Tools/Disasm/Research/Contracts.py'
    text=(ROOT/relative).read_text('utf-8')
    assert 'from IntroTextureScaleFacts import' not in text
    update(relative,text+'\nfrom IntroTextureScaleFacts import CONTRACTS as INTRO_TEXTURE_SCALE_CONTRACTS\nCONTRACTS.update(INTRO_TEXTURE_SCALE_CONTRACTS)\n')
    relative='Tools/Disasm/Research/SemanticNames.py'
    text=(ROOT/relative).read_text('utf-8')
    hook='def name_operands(region, function_address, operation):'
    assert text.count(hook)==1
    text=text.replace(hook,hook+'\n    operation = intro_texture_scale_name_operands(region, function_address, operation)')
    update(relative,text+'\nfrom IntroTextureScaleFacts import LABELS as INTRO_TEXTURE_SCALE_LABELS, name_operands as intro_texture_scale_name_operands\nLABELS.update(INTRO_TEXTURE_SCALE_LABELS)\nDOCUMENTS["Intro", 0x6C21] = ("IntroTextureScale", "масштаб текстуры")\n')
    for relative,anchor,addition in (
        ('Docs/FunctionDetails/Intro.md','[Intro.AdvanceTextureScale](../../Source/Intro/AdvanceTextureScale.asm)',
         '\n\n[Полный контракт и проверка](../IntroTextureScale.md).'),
        ('Docs/Intro.md',None,'\nТри счётчика и граница перехода к циклу описаны в [масштабе текстуры](IntroTextureScale.md).\n')):
        text=(ROOT/relative).read_text('utf-8')
        if anchor:
            assert text.count(anchor)==1
            text=text.replace(anchor,anchor+addition)
        else:text+=addition
        update(relative,text)
    candidate=ROOT/'Tools/Disasm/Research/Candidates/IntroTextureScale'
    history=ROOT/'Tools/Disasm/Research/History/BeforeIntroTextureScale'
    assert not candidate.exists() and not history.exists()
    # Сохранение кандидата и исходных контрольных копий до применения.
    for relative,(before,after) in pending.items():
        for folder,data in ((candidate,after),(history,before)):
            path=folder/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    # Проверка неизменности рабочей копии перед точечной публикацией.
    for relative,(before,_) in pending.items():assert (ROOT/relative).read_bytes()==before,relative
    for relative,(_,after) in pending.items():(ROOT/relative).write_bytes(after)
    verify()
    report=dict(passed=True,changed_files=list(pending),original_instructions_and_bytes_preserved=True,
        new_memory_allocated=False,model_cases=proof['total_cases'],assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroTextureScaleClassification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
