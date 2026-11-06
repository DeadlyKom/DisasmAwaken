"""Публикация 52 подтверждённых байтов таблицы, отдельный кандидат и точная копия прежнего ресурса."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionClassHandlersData as facts


def main():
    def read(name):return json.loads((ROOT/f'Tools/Disasm/Reports/{name}.json').read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionClassDispatchVerification')['passed'] and read('ActionClassDispatchClassification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    text,labels=facts.render(source);raw=source[0x72D:0x761];assert facts.parse(text)==(raw,labels)
    source_map,symbols,inventory=read('SourceMap'),read('Symbols'),read('Inventory')
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x72D)
    assert old['kind']=='unclassified' and old['length']==329
    previous=ROOT/old['path'];original=previous.read_bytes();assert original==source[0x72D:0x876]
    suffix='Source/Resources/17_ACTION/Unclassified007_AfterClassHandlers.bin'
    pieces=[dict(old,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest()) for start,end,kind,path,origin in (
            (0x72D,0x761,'typed_data',facts.TABLE[1],0x64F0),(0x761,0x876,'unclassified',suffix,None))]
    position=source_map.index(old);source_map[position:position+1]=pieces
    assert not any(key in symbols for key in labels);symbols.update(labels)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/facts.TABLE[1]:text.encode('utf-8'),ROOT/suffix:source[0x761:0x876]}
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/f'Tools/Disasm/Reports/{name}.json']=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FClassHandler' not in text
    block=('\n                ; Физический указатель косвенного диспетчера класса ACTION\n'
        '                struct FClassHandler\n'+
        'Handler'.ljust(16)+'dw #0000'.ljust(64)+'; исходный адрес обработчика, младший байт записан первым\n'
        '                ends\n                assert FClassHandler == #02\n\n')
    head,tail=text.rsplit('                endif',1);pending[path]=(head+block+'                endif'+tail).encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+previous.name+'"';assert text.count(needle)==1
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle,needle)
    replacement=('                disp #64F0\n                include "../Action/Data/ClassHandlers.asm"\n                ent\n'
        '                assert $ == #0761\n                ; Unknown, код после 26 указателей классов\n'
        '                incbin "../Resources/17_ACTION/Unclassified007_AfterClassHandlers.bin"')
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка трёх физических FComponent24, старших знаковых слов и сохранённых младших байтов.'
    assert text.count(needle)==1 and 'class_handler_records' not in text
    hook='''    # Проверка ровно 26 физических адресов классов, без соседних инструкций.
    from ActionClassHandlersData import TABLE as CLASS_HANDLERS, parse as parse_class_handlers
    class_handler_records = 0
    entries = [item for item in source_map if item['path'] == CLASS_HANDLERS[1]]
    if entries:
        assert len(entries) == 1
        item = entries[0]
        raw, labels = parse_class_handlers((ROOT / CLASS_HANDLERS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin']) == (17,0x72D,52,0x64F0)
        assert raw == sources[17][0x72D:0x761]
        assert all(symbols.get(key.upper()) == value for key,value in labels.items())
        assert symbols['FCLASSHANDLER'] == 2 and symbols['FCLASSHANDLER.HANDLER'] == 0
        class_handler_records = 26

'''
    text=text.replace(needle,hook+needle);needle="    report['component_work_records'] = component_work_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,"    report['class_handler_records'] = class_handler_records\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1 and 'CLASS_HANDLERS_TABLE' not in text
    hook=('    # Двадцать шесть физических указателей класса до первого RET обработчиков.\n'
        '    from ActionClassHandlersData import TABLE as CLASS_HANDLERS_TABLE, render as render_class_handlers\n'
        '    text, bindings = render_class_handlers(data_by_slot[17])\n'
        '    write(CLASS_HANDLERS_TABLE[1], text)\n    symbols.update(bindings)\n'
        '    special[17, 0x72D] = (0x761, CLASS_HANDLERS_TABLE[1], 0x64F0)\n')
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8')
    pending[path]=(text+'\n## Указатели классов ACTION\n\n[ClassHandlers](../Source/Action/Data/ClassHandlers.asm) содержит 26 физических FClassHandler размером два байта. Handler расположен по смещению 0, слова занимают 64F0..6523. Потребитель и поведение индексов вне таблицы описаны в [диспетчере](ActionClassDispatch.md). Соседние байты кода частью таблицы не являются.\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');line=next(v for v in text.splitlines() if '"| FComponent24 |' in v)
    row='| FClassHandler | #02 | Handler, 26 физических [ClassHandlers](../Source/Action/Data/ClassHandlers.asm), см. [ActionClassDispatch](ActionClassDispatch.md) |'
    pending[path]=text.replace(line,line+'\n'+line[:len(line)-len(line.lstrip())]+json.dumps(row,ensure_ascii=False)+',').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClassHandlers';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClassHandlers'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка сохранности рабочей копии перед публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},previous:original}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого сырого ресурса после проверки точного оригинала и сохранённой копии.
    assert previous.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert previous.read_bytes()==original==(history/previous.relative_to(ROOT)).read_bytes();previous.unlink()
    report=dict(passed=True,typed_bytes=52,physical_records=26,structure='FClassHandler',
        original_bytes_preserved=True,neighbor_bytes_preserved=277,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionClassHandlersClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
