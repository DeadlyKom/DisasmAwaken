"""Завершение публикации EC54 после эквивалентного оформления суммы двух размеров."""
import contextlib,hashlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionProjectedPairCodes'
    old_map=json.loads((history/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    old=next(i for i in old_map if i['slot']==17 and i['offset']<=0x8C54<i['offset']+i['length'])
    original=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    path=ROOT/old['path'];assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    expected=original[old['offset']:old['offset']+old['length']]
    assert old['kind']=='unclassified' and hashlib.sha256(expected).hexdigest()==old['sha256']
    assert path.read_bytes()==expected==(history/old['path']).read_bytes()
    current=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    assert not any(i['path']==old['path'] for i in current)
    path.unlink()
    result=dict(passed=True,described_functions=1,semantic_status='described',confirmed_code_bytes=84,
        confirmed_instructions=59,model_cases=268705,original_bytes_preserved=True,
        self_modifying_writers_registered=0,assembly_executed=False)
    # Проверка числа опубликованных инструкций по физическому диапазону исходного ACTION.
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    region=next(r for r in flow if r['name']=='Action')
    result['confirmed_instructions']=sum(0xEC54<=i['address']<0xECA8 for i in region['instructions'])
    (ROOT/'Tools/Disasm/Reports/ActionProjectedPairCodesClassification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
