"""Типизация только доказанной таблицы RET, неизвестный E291 не переименовывается."""
from collections import Counter
import contextlib
import hashlib
import io
import json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ControlsRasterReturns as facts


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert read('ControlsRasterReturnsVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    item=next(i for i in source_map if i['slot']==23 and i['offset']==0x793)
    assert (item['length'],item['kind'])==(32,'unclassified')
    previous=ROOT/item['path']
    original=previous.read_bytes()
    assert original==source[0x793:0x7B3]
    text,bindings=facts.render(source)
    assert facts.parse(text)==(original,bindings)
    assert not any(name in symbols for name in bindings)
    symbols.update(bindings)
    item.update(kind='typed_data',path=facts.TABLE[1],origin=0xE271,sha256=hashlib.sha256(original).hexdigest())
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind)
                                       for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8')}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc'
    text=path.read_text('utf-8')
    assert 'struct FReturnDispatchEntry' not in text
    block=('\n                ; Физический адрес для RET с временно выбранным табличным SP\n'
        '                struct FReturnDispatchEntry\n'
        'Target          dw #0000                                                        ; адрес кодового хвоста в том же банке\n'
        '                ends\n                assert FReturnDispatchEntry == 2\n\n')
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/23_CONTROL.inc'
    text=path.read_text('utf-8')
    needle=('                ; Unknown, следующая таблица указателей ещё не разобрана\n'
        '                incbin "../Resources/23_CONTROL/Unclassified004_AfterGlyphs.bin"')
    assert text.count(needle)==1
    replacement=('                ; Физические адреса для перенаправленного RET, полный рисователь ещё Unknown\n'
        '                disp #E271\n                include "../Controls/Data/RasterReturns.asm"\n                ent')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py'
    text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook=('    # Шестнадцать исходных адресов для диспетчеризации через RET, полного разбора хвостов нет.\n'
        '    if "struct FReturnDispatchEntry" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):\n'
        '        from ControlsRasterReturns import TABLE as RASTER_RETURNS, render as render_raster_returns\n'
        '        text, bindings = render_raster_returns(data_by_slot[23])\n'
        '        write(RASTER_RETURNS[1], text)\n        symbols.update(bindings)\n'
        '        special[23, 0x793] = (0x7B3, RASTER_RETURNS[1], 0xE271)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py'
    text=path.read_text('utf-8')
    needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    assert text.count(needle)==1
    hook='''    # Проверка шестнадцати физических адресов для RET, смысл полных хвостов не подменяется этой проверкой.
    from ControlsRasterReturns import TABLE as RASTER_RETURNS, parse as parse_raster_returns
    raster_return_records = 0
    entries = [item for item in source_map if item['path'] == RASTER_RETURNS[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw,labels = parse_raster_returns((ROOT/RASTER_RETURNS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (23,0x793,32,0xE271)
        assert raw == sources[23][0x793:0x7B3]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FRETURNDISPATCHENTRY'] == 2 and symbols['FRETURNDISPATCHENTRY.TARGET'] == 0
        raster_return_records = 16

'''
    text=text.replace(needle,hook+needle)
    needle="    report['three_row_glyph_records'] = three_row_glyph_records"
    assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['raster_return_records'] = raster_return_records").encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ControlsRasterReturns'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsRasterReturns'
    assert not candidate.exists() and not history.exists()
    # Создание отдельного кандидата и проверка отсутствия новых ручных изменений.
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
    # Удаление заменённого ресурса только после подтверждения сохранённого оригинала.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/23_CONTROL').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes()
    previous.unlink()
    result=dict(passed=True,typed_bytes=32,physical_records=16,structure='FReturnDispatchEntry',
        physical_bytes_preserved=True,selected_tails_proved=False,unknown_e291_status_preserved=True,
        assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRasterReturnsClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
