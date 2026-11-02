"""Типизация исходных 512 байтов квадратов, без пересоздания значений формулой."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
import ControlsSquareTable as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsSquaresVerification')['passed']
    source = bytes(base_memory()[0xC000:0xDADE])
    raw = facts.validate(source)
    text,labels = facts.render(source)
    assert facts.parse(text) == (raw,labels)
    source_map,symbols,inventory = read('SourceMap'),read('Symbols'),read('Inventory')
    item = next(i for i in source_map if i['slot']==22 and i['offset']==0)
    assert (item['length'],item['kind']) == (0x500,'unclassified')
    previous = ROOT/item['path']
    original = previous.read_bytes()
    assert original == source[:0x500]
    prefix = 'Source/Resources/22_CONTROL0/Unclassified000_BeforeSquares.bin'
    pieces = [dict(slot=22,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
            (0,0x300,'unclassified',prefix,None),(0x300,0x500,'typed_data',facts.TABLE[1],0xC300))]
    index = source_map.index(item)
    source_map[index:index+1] = pieces
    assert not any(key in symbols for key in labels)
    symbols.update(labels)
    inventory['ranges_by_kind'] = dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind'] = {kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending = {ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/prefix:source[:0x300]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Includes/Structs/Include.inc'
    text = path.read_text('utf-8')
    assert 'struct FSquareTableByte' not in text
    block = ('\n                ; Физический байт одной из двух разрядных плоскостей квадрата\n'
        '                struct FSquareTableByte\n'
        'Value           db #00                                                          ; младший либо старший байт, часть указана именем экземпляра\n'
        '                ends\n                assert FSquareTableByte == 1\n\n')
    pending[path] = text.replace('                endif',block+'                endif').encode('utf-8')
    path = ROOT/'Source/Files/22_CONTROL0.inc'
    text = path.read_text('utf-8')
    needle = '                incbin "../Resources/22_CONTROL0/Unclassified000_Prefix.bin"'
    assert text.count(needle)==1
    replacement = ('                incbin "../Resources/22_CONTROL0/Unclassified000_BeforeSquares.bin"\n'
        '                assert $ == #0300\n                disp #C300\n'
        '                include "../Controls/Data/Squares.asm"\n                ent')
    pending[path] = text.replace(needle,replacement).encode('utf-8')
    path = ROOT/'Tools/Disasm/Research/ExportSources.py'
    text = path.read_text('utf-8')
    needle = '    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook = ('    # Две исходные плоскости квадратов оформляются по физическим байтам CONTROL0.\n'
        '    if "struct FSquareTableByte" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsSquareTable import TABLE as SQUARE_TABLE, render as render_squares\n'
        '        text, bindings = render_squares(data_by_slot[22])\n'
        '        write(SQUARE_TABLE[1], text)\n        symbols.update(bindings)\n'
        '        special[22, 0x300] = (0x500, SQUARE_TABLE[1], 0xC300)\n')
    pending[path] = text.replace(needle,hook+needle).encode('utf-8')
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ControlsSquareTable'
    history = ROOT/'Tools/Disasm/Research/History/BeforeControlsSquareTable'
    assert not candidate.exists() and not history.exists()
    # Создание кандидата, проверка рабочей копии и сохранение всех заменяемых версий.
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target = candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target = history/path.relative_to(ROOT)
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
    report = dict(passed=True,typed_bytes=512,physical_records=512,square_indices=256,
        low_plane='C300',high_plane='C400',all_original_values_match_squares=True,
        formula_used_to_regenerate_build_data=False,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSquareTableClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
