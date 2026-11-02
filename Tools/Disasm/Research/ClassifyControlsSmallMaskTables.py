"""Типизация ровно 30 подтверждённых байтов, оставшиеся 20 сохраняются неизвестными."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
import ControlsSmallMaskTables as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsSmallMasksVerification')['passed']
    source=bytes(base_memory()[0xC000:0xDADE])
    facts.validate(source)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==22 and i['offset']==0x197E)
    assert (item['length'],item['kind'])==(50,'unclassified')
    previous=ROOT/item['path']
    original=previous.read_bytes()
    assert original==source[0x197E:0x19B0]
    suffix='Source/Resources/22_CONTROL0/Unclassified011_AfterMasks.bin'
    pending={ROOT/suffix:source[0x199C:0x19B0]}
    pieces=[]
    for table in facts.TABLES:
        text,labels=facts.render(source,table)
        assert facts.parse(text,table)==(source[table[2]:table[3]],labels)
        assert not any(key in symbols for key in labels)
        symbols.update(labels)
        pending[ROOT/table[1]]=text.encode('utf-8')
        pieces.append(dict(slot=22,offset=table[2],length=table[3]-table[2],kind='typed_data',path=table[1],
            origin=0xC000+table[2],sha256=hashlib.sha256(source[table[2]:table[3]]).hexdigest()))
    pieces.append(dict(slot=22,offset=0x199C,length=20,kind='unclassified',path=suffix,origin=None,
        sha256=hashlib.sha256(source[0x199C:0x19B0]).hexdigest()))
    index=source_map.index(item)
    source_map[index:index+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc'
    text=path.read_text('utf-8')
    assert 'struct FSmallMaskSeed' not in text and 'struct FSmallMaskRow' not in text
    block=('\n                ; Физическая упакованная затравка масок малых тел\n'
        '                struct FSmallMaskSeed\n'
        'Packed          db #00                                                          ; начальная маска в разрядах 7..3, число сдвигов в 2..0\n'
        '                ends\n                assert FSmallMaskSeed == 1\n\n'
        '                ; Физическая строковая маска, изменяемая исходным подготовителем\n'
        '                struct FSmallMaskRow\n'
        'Mask            db #00                                                          ; исходный ноль до подготовки малой фигуры\n'
        '                ends\n                assert FSmallMaskRow == 1\n\n')
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/22_CONTROL0.inc'
    text=path.read_text('utf-8')
    needle='                incbin "../Resources/22_CONTROL0/Unclassified011.bin"'
    assert text.count(needle)==1
    replacement=('                disp #D97E\n                include "../Controls/Data/SmallMaskSeeds.asm"\n                ent\n'
        '                assert $ == #1990\n                disp #D990\n                include "../Controls/Data/SmallMaskRows.asm"\n                ent\n'
        '                assert $ == #199C\n                ; Unknown, назначение следующих 20 исходных байтов отдельно не установлено\n'
        '                incbin "../Resources/22_CONTROL0/Unclassified011_AfterMasks.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook=('    # Исходные затравки и известная часть записываемых строковых масок.\n'
        '    if "struct FSmallMaskSeed" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsSmallMaskTables import TABLES as SMALL_MASK_TABLES, render as render_small_mask\n'
        '        for table in SMALL_MASK_TABLES:\n'
        '            text, bindings = render_small_mask(data_by_slot[22], table)\n'
        '            write(table[1], text)\n            symbols.update(bindings)\n'
        '            special[22, table[2]] = (table[3], table[1], 0xC000+table[2])\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsSmallMaskTables'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsSmallMaskTables'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и проверка текущих версий перед записью.
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
    result=dict(passed=True,typed_bytes=30,seed_records=18,row_records=12,remaining_unknown_bytes=20,
        original_zero_initializers_preserved=True,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSmallMaskTablesClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
