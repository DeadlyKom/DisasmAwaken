"""Физические вложенные экземпляры исходных слотов, известные поля и явные Unknown, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
import ActionObjectRecords as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionObjectRecordsResearchVerification');assert proof['passed'] and proof['physical_bytes']==1664
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3D82)
    assert old['kind']=='unclassified' and old['length']==0xAAB
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x3D82:0x482D]
    text,bindings=facts.render(source);assert facts.parse(text)==(source[facts.START:facts.END],bindings)
    assert not any(k in symbols for k in bindings);symbols.update(bindings)
    prefix='Source/Resources/17_ACTION/Unclassified020_BeforeObjectRecords.bin'
    suffix='Source/Resources/17_ACTION/Unclassified020_AfterObjectRecords.bin'
    pending={ROOT/facts.PATH:text.encode('utf-8'),ROOT/prefix:source[0x3D82:0x4100],ROOT/suffix:source[0x4780:0x482D]}
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    index=source_map.index(old);source_map[index:index+1]=[piece(0x3D82,0x4100,'unclassified',prefix,None),
        piece(0x4100,0x4780,'typed_data',facts.PATH,0xA100),piece(0x4780,0x482D,'unclassified',suffix,None)]
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FActionRecord' not in text
    pending[path]=text.replace('                endif',facts.structure_text()+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    repl='                incbin "../Resources/17_ACTION/'+prefix.rsplit('/',1)[-1]+'"\n                assert $ == #4100\n                disp #A100\n'
    repl+='                include "../Action/Data/ObjectRecords.asm"\n                ent\n                assert $ == #4780\n'
    repl+='                ; Unknown, соседнее состояние A780..A82C ещё не разобрано\n                incbin "../Resources/17_ACTION/'+suffix.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,repl).encode('utf-8')
    # Именование только доказанных индексных полей трёх опубликованных читателей.
    for name in ('FindReusableRecord','NextActiveRecord','FindRecordByCode'):
        path=ROOT/('Source/Action/'+name+'.asm');text=path.read_text('utf-8')
        for number,field in (('00','Components.Component0.Low'),('01','Components.Component0.High'),('12','ClassCode'),('18','ReuseByte')):
            text=text.replace('(IY + #'+number+')','(IY + FActionRecord.'+field+')')
        pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Начальные 25 записей и отдельный маркер, реальные вложенные экземпляры.
    if "struct FActionRecord" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionObjectRecords import PATH as OBJECT_RECORDS, render as render_object_records
        text,bindings=render_object_records(data_by_slot[17])
        write(OBJECT_RECORDS,text)
        symbols.update(bindings)
        special[17,0x4100]=(0x4780,OBJECT_RECORDS,0xA100)
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.';assert text.count(needle)==1
    hook='''    # Проверка всех байтов физических записей и вложенных смещений по реальным STRUCT.
    from ActionObjectRecords import PATH as OBJECT_RECORDS, parse as parse_object_records, SCHEMA as OBJECT_STRUCTS, layout as object_layout
    object_records=0
    entries=[i for i in source_map if i['path']==OBJECT_RECORDS]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_object_records((ROOT/OBJECT_RECORDS).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x4100,1664,0xA100)
        assert raw==sources[17][0x4100:0x4780]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        for structure in OBJECT_STRUCTS:
            size,fields=object_layout(structure)
            assert symbols[structure.upper()]==size
            assert all(symbols.get((structure+'.'+field).upper())==value for field,value in fields.items())
        object_records=26

'''
    text=text.replace(needle,hook+needle);needle="    report['type_delta_records'] = type_delta_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['action_object_records'] = object_records").encode('utf-8')
    for filename,addresses in (('ActionRecordSearchFacts.py',(0xE9A1,)),('ActionRecordIteratorFacts.py',(0xE6D1,0xE98D))):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');needle='def name_operands(region,function_address,operation):'
        if filename=='ActionRecordSearchFacts.py':
            assert text.count(needle+'return operation')==1;text=text.replace(needle+'return operation',needle+'\n    return operation')
        assert text.count(needle)==1
        hook="\n    if region=='Action' and function_address in "+repr(addresses)+":\n"
        for number,field in (('00','Components.Component0.Low'),('01','Components.Component0.High'),('12','ClassCode'),('18','ReuseByte')):
            hook+="        operation=operation.replace('(IY + #"+number+")','(IY + FActionRecord."+field+")')\n"
        pending[path]=text.replace(needle,needle+hook).encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8');needle='| FIndexedDelta |';assert text.count(needle)==1
    row='| FActionRecord | #40 | 25 физических исходных слотов и маркер, вложенные компоненты и явные неизвестные поля, см. [ActionObjectRecords](ActionObjectRecords.md) |\n'
    pending[path]=text.replace(needle,row+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8');needle='               "| FIndexedDelta |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'               '+repr(row.rstrip()).replace("'",'"')+',\n'+needle).encode('utf-8')
    for filename in ('ActionRecordSearch.md','ActionRecordIterator.md','ActionRecordIndex.md'):
        path=ROOT/'Docs'/filename;text=path.read_text('utf-8');text+='\n[Физические начальные записи и вложенные поля](ActionObjectRecords.md) оформлены отдельно. Начальные 25 слотов и маркер не подменяют доказательство всех динамических состояний.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionObjectRecords';history=ROOT/'Tools/Disasm/Research/History/BeforeActionObjectRecords';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка новых правок до записи.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого ресурса после сохранения и побайтовой сверки.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x3D82:0x482D]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,typed_bytes=1664,physical_records=26,initial_slots=25,marker_separate=True,
        nested_structure_sizes=[2,6,64],physical_symbol_bindings=len(bindings),physical_bytes_preserved=True,
        all_field_game_meanings_proved=False,runtime_array_limit_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectRecordsClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
