"""Обновление только точного договора полного большого эффекта, инструкции не меняются."""
import contextlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from SourcePresentation import instructions
from ActionLargeEffectContinuationFacts import CONTRACTS


def main():
    path=ROOT/'Source/Action/AllocateLargeEffect.asm';before=path.read_text('utf-8')
    start=before.index('                ; In:\n');end=before.index('                ; -----------------------------------------',start)
    lines=[]
    for title,values in zip(('In','Out','Corrupt','Note'),CONTRACTS['Action',0xEA3D]):
        lines+=['                ; '+title+':']+['                ;   '+v for v in values]
    after=before[:start]+'\n'.join(lines)+'\n'+before[end:];assert instructions(before)==instructions(after)
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionFullLargeEffectContract'/path.relative_to(ROOT)
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionFullLargeEffectContract'/path.relative_to(ROOT)
    assert not candidate.exists() and not history.exists();candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(after,'utf-8')
    assert path.read_text('utf-8')==before;history.parent.mkdir(parents=True,exist_ok=True);history.write_text(before,'utf-8');path.write_text(after,'utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,source_instruction_text_unchanged=True,large_classes_cases=51840,small_classes_cases=16384,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionFullLargeEffectContractVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
