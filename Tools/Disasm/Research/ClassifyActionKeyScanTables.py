"""Контролируемая типизация 106 байтов и одного RET, без массового декодирования обработчиков."""
from collections import Counter
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
import ActionKeyScanTables as tables
import ActionIgnoreKeyFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionKeyDispatchPrefixVerification')['passed'] and read('ActionIgnoreKeyVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert source[0x1288:0x128A]==bytes.fromhex('c9 c0')
    assert source[0x3D4C:0x3D4E]==source[0x3D80:0x3D82]
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    first=next(i for i in source_map if i['slot']==17 and i['offset']==0x1254)
    second=next(i for i in source_map if i['slot']==17 and i['offset']==0x3C12)
    assert (first['length'],first['kind'])==(0x4E4,'unclassified')
    assert (second['length'],second['kind'])==(0xC1B,'unclassified')
    previous={ROOT/i['path']:(i['offset'],i['length']) for i in (first,second)}
    for path,(start,length) in previous.items():assert path.read_bytes()==source[start:start+length]
    pending={}
    for table in tables.TABLES:
        text,bindings=tables.render(source,table)
        assert tables.parse(text,table)==(source[table[2]:table[3]],bindings)
        assert not any(key in symbols for key in bindings)
        assert not (ROOT/table[1]).exists()
        symbols.update(bindings);pending[ROOT/table[1]]=text.encode('utf-8')
    code_path='Source/Action/IgnoreKey.asm'
    suffix='Source/Resources/17_ACTION/Unclassified017_AfterIgnoreKey.bin'
    prefix_keys='Source/Resources/17_ACTION/Unclassified020_BeforeKeyInputs.bin'
    suffix_keys='Source/Resources/17_ACTION/Unclassified020_AfterKeyInputs.bin'
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    index=source_map.index(first)
    source_map[index:index+1]=[
        piece(0x1254,0x1288,'typed_data',tables.TABLES[0][1],0x7017),piece(0x1288,0x1289,'code',code_path,0x704B),
        piece(0x1289,0x1738,'unclassified',suffix,None)]
    index=source_map.index(second)
    source_map[index:index+1]=[
        piece(0x3C12,0x3D4C,'unclassified',prefix_keys,None),piece(0x3D4C,0x3D82,'typed_data',tables.TABLES[1][1],0x9D4C),
        piece(0x3D82,0x482D,'unclassified',suffix_keys,None)]
    pending.update({ROOT/suffix:source[0x1289:0x1738],ROOT/prefix_keys:source[0x3C12:0x3D4C],ROOT/suffix_keys:source[0x3D82:0x482D]})
    name,description=facts.FUNCTIONS[0x704B]
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']==0x6F55)+1
    functions.insert(index,dict(region='Action',name=name,address=0x704B,slot=17,offset=0x1288,
        description=description,semantic_status='described',end_offset=0x1289,path=code_path))
    assert 'Action.IgnoreKey.Entry' not in symbols
    symbols['Action.IgnoreKey.Entry']=0x704B
    region=next(r for r in flow if r['name']=='Action')
    assert not any(i['address']==0x704B for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+[dict(address=0x704B,operation='RET',hex='c9',slot=17,offset=0x1288)],key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0x704B});region['instruction_count']+=1;region['code_bytes']+=1
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+1)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    lines=['                module Action','                module IgnoreKey',
        '                ; Документация [пустой обработчик клавиши](../../Docs/ActionKeyDispatchPrefix.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, банк 5, адрес 704B, файловое смещение 1288']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x704B]):
        lines+=['                ; '+heading+':']+['                ;   '+value for value in values]
    lines+=['                ; -----------------------------------------','Entry:          RET','','                endmodule','                endmodule']
    pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Source/Action/Unknown6F1D.asm';text=path.read_text('utf-8')
    assert text.count('LD IX, #9D4C')==1 and text.count('LD DE, #7015')==1
    pending[path]=text.replace('LD IX, #9D4C','LD IX, @ActionKeyScanInputs.Index00.RowSelect').replace(
        'LD DE, #7015','LD DE, @ActionKeyHandlerPointers.Index00 - 2').encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');block='\n'
    for table in tables.TABLES:
        structure=table[4];assert 'struct '+structure not in text
        block+='                ; Физическая запись частично разобранного клавиатурного диспетчера\n                struct '+structure+'\n'
        for field,width,note in table[5]:block+=field.ljust(16)+('dw #0000' if width==2 else 'db #00').ljust(64)+'; '+note+'\n'
        block+='                ends\n                assert '+structure+' == 2\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    first_path=next(path for path,(start,length) in previous.items() if start==0x1254)
    needle='                incbin "../Resources/17_ACTION/'+first_path.name+'"';assert text.count(needle)==1
    replacement='                disp #7017\n                include "../Action/Data/KeyHandlerPointers.asm"\n                ent\n'
    replacement+='                assert $ == #1288\n                disp #704B\n                include "../Action/IgnoreKey.asm"\n                ent\n'
    replacement+='                assert $ == #1289\n                ; Unknown, остальные обработчики ещё не разобраны\n                incbin "../Resources/17_ACTION/'+suffix.rsplit('/',1)[-1]+'"'
    text=text.replace(needle,replacement)
    second_path=next(path for path,(start,length) in previous.items() if start==0x3C12)
    needle='                incbin "../Resources/17_ACTION/'+second_path.name+'"';assert text.count(needle)==1
    replacement='                incbin "../Resources/17_ACTION/'+prefix_keys.rsplit('/',1)[-1]+'"\n'
    replacement+='                assert $ == #3D4C\n                disp #9D4C\n                include "../Action/Data/KeyScanInputs.asm"\n                ent\n'
    replacement+='                assert $ == #3D82\n                ; Unknown, соседние данные ещё не разобраны\n                incbin "../Resources/17_ACTION/'+suffix_keys.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionIgnoreKeyFacts import FUNCTIONS as ACTION_IGNORE_KEY_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_IGNORE_KEY_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionIgnoreKeyFacts import CONTRACTS as ACTION_IGNORE_KEY_CONTRACTS\nCONTRACTS.update(ACTION_IGNORE_KEY_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_key_scan_tables_name_operands(region,function_address,operation)')
    text+="\nfrom ActionKeyScanTables import name_operands as action_key_scan_tables_name_operands\nDOCUMENTS['Action',0x704B]=('ActionKeyDispatchPrefix','пустой обработчик клавиши')\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    assert text.count(needle)==1
    hook='''    # Первые 26 отдельных указателей и 27 физических пар порта и маски, без дублирования кода 704B.
    if "struct FKeyScanInput" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionKeyScanTables import TABLES as KEY_SCAN_TABLES, render as render_key_scan_table, origin as key_scan_origin
        for table in KEY_SCAN_TABLES:
            text,bindings=render_key_scan_table(data_by_slot[17],table)
            write(table[1],text)
            symbols.update(bindings)
            special[17,table[2]]=(table[3],table[1],key_scan_origin(table)+table[2])
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    hook='''    # Проверка 26 отдельных указателей и 27 пар IN, перекрывающееся слово 704B/704C не эмитируется повторно.
    from ActionKeyScanTables import TABLES as KEY_SCAN_TABLES, parse as parse_key_scan_table, origin as key_scan_origin
    key_scan_records=0
    for table in KEY_SCAN_TABLES:
        entries=[item for item in source_map if item['path']==table[1]]
        if entries:
            assert len(entries)==1
            item=entries[0]
            raw,labels=parse_key_scan_table((ROOT/table[1]).read_text('utf-8'),table)
            assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,table[2],table[3]-table[2],key_scan_origin(table)+table[2])
            assert raw==sources[17][table[2]:table[3]]
            assert all(symbols.get(key.upper())==value for key,value in labels.items())
            assert symbols[table[4].upper()]==2
            offset=0
            for field,width,note in table[5]:
                assert symbols[table[4].upper()+'.'+field.upper()]==offset
                offset+=width
            key_scan_records+=len(table[6])

'''
    assert text.count(needle)==1;text=text.replace(needle,hook+needle)
    needle="    report['preferred_byte_records'] = preferred_byte_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['key_scan_records'] = key_scan_records").encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions)
    described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #74FB |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #704B | [Action.IgnoreKey](../Source/Action/IgnoreKey.asm) | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## SelectFuelStock\n';assert text.count(needle)==1
    section='## IgnoreKey\n\n[Action.IgnoreKey](../../Source/Action/IgnoreKey.asm)\n\n'+description+'.\n\nВход `#704B`, запись 17, смещение `#1288`.\n\n[Вызов, возврат и перекрытие последнего указателя](../ActionKeyDispatchPrefix.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionKeyScanTables';history=ROOT/'Tools/Disasm/Research/History/BeforeActionKeyScanTables'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и сверка актуальности всех затрагиваемых файлов до публикации.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},**{p:p.read_bytes() for p in previous}}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только двух заменённых ресурсов после сравнения с сохранёнными оригиналами.
    for path,(start,length) in previous.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes()==source[start:start+length]==(history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    report=dict(passed=True,typed_bytes=106,physical_pointer_records=26,physical_input_records=27,
        confirmed_code_bytes=1,confirmed_instructions=1,described_functions=1,
        physical_bytes_preserved=True,last_overlapping_pointer_not_duplicated=True,
        unknown_dispatcher_status_preserved=True,other_handlers_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionKeyScanTablesClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
