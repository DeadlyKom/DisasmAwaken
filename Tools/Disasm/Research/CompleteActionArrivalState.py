"""Завершение публикации State08 после привязки к реальному физическому имени Unknown15."""
import contextlib,hashlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    source=ROOT/'Source/Action/ApproachTargetRecordAndResolve.asm'
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionArrivalState/Source/Action/ApproachTargetRecordAndResolve.asm'
    before=candidate.read_text('utf-8');after=before.replace('OverrideLink','Unknown15')
    assert after==source.read_text('utf-8');candidate.write_text(after,'utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionArrivalState'
    old_map=json.loads((history/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    old=next(p for p in old_map if p['slot']==17 and p['offset']<=0x957F<p['offset']+p['length'])
    data=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    expected=data[old['offset']:old['offset']+old['length']];old_path=ROOT/old['path']
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==expected==(history/old['path']).read_bytes()
    assert hashlib.sha256(expected).hexdigest()==old['sha256'];old_path.unlink()
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if 0xF57F<=i['address']<0xF66A]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==data[0x957F:0x966A]
    result=dict(passed=True,described_functions=1,semantic_status='described',confirmed_code_bytes=235,
        confirmed_instructions=len(records),model_cases=70256,original_bytes_preserved=True,
        self_modifying_writers_registered=3,assembly_executed=False)
    reports=ROOT/'Tools/Disasm/Reports'
    (reports/'ActionArrivalStateClassification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    assert data[0x8F60:0x8F62]==bytes((0x7F,0xF5))
    binding=dict(passed=True,state_index=8,address=0xF57F,name='ApproachTargetRecordAndResolve',physical_pointer_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ActionArrivalStateBindingClassification.json').write_text(json.dumps(binding,indent=2)+'\n','utf-8')
    print(json.dumps(result,indent=2));print(json.dumps(binding,indent=2))


if __name__=='__main__':main()
