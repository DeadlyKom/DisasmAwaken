"""Однократное оформление семи исходных байтов шкалы, без сборки."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ControlsGaugeMasks as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ControlsSixRowGaugeVerification')['passed'] and read('ControlsSixRowGaugeClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==23 and i['offset']==0xE95)
    assert (item['length'],item['kind'],item['path'])==(7,'unclassified','Source/Resources/23_CONTROL/Unclassified006.bin')
    previous=ROOT/item['path'];original=previous.read_bytes()
    assert original==source[0xE95:0xE9C]
    text,bindings=facts.render(source)
    assert facts.parse(text)==(original,bindings)
    assert not any(key in symbols for key in bindings)
    symbols.update(bindings)
    assert not (ROOT/facts.TABLE[1]).exists()
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8')}
    item.update(kind='typed_data',path=facts.TABLE[1],origin=0xE973,sha256=hashlib.sha256(original).hexdigest())
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
        for kind in inventory['ranges_by_kind']}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    assert 'struct FGaugePartialMask' not in text
    block='\n                ; Физическая маска частичного столбца шестистрочной шкалы\n                struct FGaugePartialMask\n'
    block+='Pattern         '+('db #00').ljust(64)+'; исходный байт для шести строк частичного столбца\n'
    block+='                ends\n                assert FGaugePartialMask == 1\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/23_CONTROL.inc';text=path.read_text('utf-8')
    needle=('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/23_CONTROL/Unclassified006.bin"')
    assert text.count(needle)==1
    pending[path]=text.replace(needle,'                ; Семь физических масок частичного столбца шкалы\n'
        '                disp #E973\n                include "../Controls/Data/GaugeMasks.asm"\n                ent').encode('utf-8')
    path=ROOT/'Source/Controls/DrawSixRowGauge.asm';text=path.read_text('utf-8')
    assert text.count('LD HL, #E973')==1
    pending[path]=text.replace('LD HL, #E973','LD HL, @ControlsGaugeMasks.Index00').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook='''    # Семь физических масок шестистрочной шкалы.
    if "struct FGaugePartialMask" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ControlsGaugeMasks import TABLE as GAUGE_MASKS, render as render_gauge_masks
        text,bindings=render_gauge_masks(data_by_slot[23])
        write(GAUGE_MASKS[1],text)
        symbols.update(bindings)
        special[23,0xE95]=(0xE9C,GAUGE_MASKS[1],0xE973)
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle)==1
    hook='''    # Проверка семи физических масок частичного столбца шкалы.
    from ControlsGaugeMasks import TABLE as GAUGE_MASKS, parse as parse_gauge_masks
    gauge_mask_records=0
    entries=[item for item in source_map if item['path']==GAUGE_MASKS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_gauge_masks((ROOT/GAUGE_MASKS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(23,0xE95,7,0xE973)
        assert raw==sources[23][0xE95:0xE9C]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FGAUGEPARTIALMASK']==1 and symbols['FGAUGEPARTIALMASK.PATTERN']==0
        gauge_mask_records=7

'''
    text=text.replace(needle,hook+needle)
    needle="    report['object_glyph_records'] = object_glyph_records"
    assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['gauge_mask_records'] = gauge_mask_records").encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsGaugeMasks'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsGaugeMasks'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка актуальности рабочей копии перед записью.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление заменённого бинарного файла после сравнения с сохранённым оригиналом.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    report=dict(passed=True,typed_bytes=7,physical_records=7,unused_by_this_consumer_indices=[0],
        physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsGaugeMasksClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
