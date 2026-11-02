"""Типизация только четырёх подтверждённых входных байтов, 12 рабочих байтов сохраняются неизвестными."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
import ControlsBodyProjection as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsSmallBodiesVerification')['passed']
    source=bytes(base_memory()[0xC000:0xDADE])
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==22 and i['offset']==0x117D)
    assert (item['length'],item['kind'])==(16,'unclassified')
    previous=ROOT/item['path']
    original=previous.read_bytes()
    assert original==source[0x117D:0x118D]==bytes(16)
    text,labels=facts.render(source)
    assert facts.parse(text)==(original[:4],labels)
    assert not any(key in symbols for key in labels)
    symbols.update(labels)
    suffix='Source/Resources/22_CONTROL0/Unclassified004_AfterProjection.bin'
    pieces=[dict(slot=22,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
            (0x117D,0x1181,'typed_data',facts.TABLE[1],0xD17D),(0x1181,0x118D,'unclassified',suffix,None))]
    index=source_map.index(item)
    source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/suffix:original[4:]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc'
    text=path.read_text('utf-8')
    assert 'struct FBodyProjection' not in text
    block='\n                ; Физические входные байты проекции объекта в банке 1\n                struct FBodyProjection\n'
    for name,width,note in facts.FIELDS:
        block+=name.ljust(16)+('db #00').ljust(64)+'; '+note+'\n'
    block+='                ends\n                assert FBodyProjection == 4\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/22_CONTROL0.inc'
    text=path.read_text('utf-8')
    needle='                incbin "../Resources/22_CONTROL0/Unclassified004.bin"'
    assert text.count(needle)==1
    replacement=('                disp #D17D\n                include "../Controls/Data/BodyProjection.asm"\n                ent\n'
        '                assert $ == #1181\n                ; Unknown, следующие 12 рабочих байтов сохраняются отдельно\n'
        '                incbin "../Resources/22_CONTROL0/Unclassified004_AfterProjection.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook=('    # Четыре физических входных байта проекции, остальные рабочие байты не типизируются формально.\n'
        '    if "struct FBodyProjection" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsBodyProjection import TABLE as BODY_PROJECTION, render as render_body_projection\n'
        '        text, bindings = render_body_projection(data_by_slot[22])\n'
        '        write(BODY_PROJECTION[1], text)\n        symbols.update(bindings)\n'
        '        special[22, 0x117D] = (0x1181, BODY_PROJECTION[1], 0xD17D)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsBodyProjection'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsBodyProjection'
    assert not candidate.exists() and not history.exists()
    # Подготовка отдельного кандидата и сохранение прежних версий перед заменой.
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/22_CONTROL0').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result=dict(passed=True,typed_bytes=4,physical_records=1,structure='FBodyProjection',
        other_flag_bits_unproved=True,remaining_work_bytes_unknown=12,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsBodyProjectionClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
