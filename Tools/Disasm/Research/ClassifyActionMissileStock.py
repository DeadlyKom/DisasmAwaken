"""Однократная публикация девяти байтов кода и двух байтов остатка ракет."""
from collections import Counter
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
import ActionMissileStockFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionMissileStockVerification');assert proof['passed'] and proof['total_cases']==65536
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert source[0x132A:0x1333]==bytes.fromhex('21 13 9c 7e a7 c0 2b 7e c9')
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    code_old=next(i for i in source_map if i['slot']==17 and i['offset']==0x1289)
    data_old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3C12)
    assert (code_old['length'],code_old['kind'])==(0x4AF,'unclassified')
    assert (data_old['length'],data_old['kind'])==(0x13A,'unclassified')
    previous={ROOT/i['path']:(i['offset'],i['length']) for i in (code_old,data_old)}
    for path,(start,length) in previous.items():assert path.read_bytes()==source[start:start+length]
    code_path='Source/Action/SelectMissileStock.asm'
    code_prefix='Source/Resources/17_ACTION/Unclassified017_BeforeMissileStock.bin'
    code_suffix='Source/Resources/17_ACTION/Unclassified017_AfterMissileStock.bin'
    data_suffix='Source/Resources/17_ACTION/Unclassified020_AfterMissileStock.bin'
    data_text,bindings=facts.render(source)
    assert facts.parse(data_text)==(source[0x3C12:0x3C14],bindings)
    assert not any(key in symbols for key in bindings)
    symbols.update(bindings)
    assert 'Action.SelectMissileStock.Entry' not in symbols
    symbols['Action.SelectMissileStock.Entry']=0x70ED
    pending={ROOT/facts.TABLE[1]:data_text.encode('utf-8'),ROOT/code_prefix:source[0x1289:0x132A],
        ROOT/code_suffix:source[0x1333:0x1738],ROOT/data_suffix:source[0x3C14:0x3D4C]}
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    index=source_map.index(code_old)
    source_map[index:index+1]=[piece(0x1289,0x132A,'unclassified',code_prefix,None),
        piece(0x132A,0x1333,'code',code_path,0x70ED),piece(0x1333,0x1738,'unclassified',code_suffix,None)]
    index=source_map.index(data_old)
    source_map[index:index+1]=[piece(0x3C12,0x3C14,'typed_data',facts.TABLE[1],0x9C12),
        piece(0x3C14,0x3D4C,'unclassified',data_suffix,None)]
    records=[dict(address=a,operation=op,hex=raw,slot=17,offset=offset) for a,op,raw,offset in (
        (0x70ED,'LD HL,#9C13','21139c',0x132A),(0x70F0,'LD A,(HL)','7e',0x132D),
        (0x70F1,'AND A','a7',0x132E),(0x70F2,'RET NZ','c0',0x132F),
        (0x70F3,'DEC HL','2b',0x1330),(0x70F4,'LD A,(HL)','7e',0x1331),(0x70F5,'RET','c9',0x1332))]
    region=next(r for r in flow if r['name']=='Action')
    assert not any(0x70ED<=i['address']<0x70F6 for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0x70ED});region['instruction_count']+=7;region['code_bytes']+=9
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    name,description=facts.FUNCTIONS[0x70ED]
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']==0x74FB)
    functions.insert(index,dict(region='Action',name=name,address=0x70ED,slot=17,offset=0x132A,
        description=description,semantic_status='described',end_offset=0x1333,path=code_path))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+7)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    lines=['                module Action','                module '+name,
        '                ; Документация [остаток ракет](../../Docs/ActionMissileStock.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, банк 5, перенесённые 70ED..70F5, смещения 132A..1332']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x70ED]):
        lines+=['                ; '+heading+':']+['                ;   '+value for value in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        before,right=facts.COMMENTS.get(record['address'],([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0x70ED,record['operation'].replace(',',', '))
        line=('Entry:          ' if record['address']==0x70ED else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule']
    pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FMissileStock' not in text
    block='\n                ; Два исходных счётчика ракет в обратном порядке приоритета\n                struct FMissileStock\n'
    for field,width,note in facts.FIELDS:block+=field.ljust(16)+('db #00').ljust(64)+'; '+note+'\n'
    block+='                ends\n                assert FMissileStock == 2\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    old_code=next(p for p,(start,length) in previous.items() if start==0x1289)
    needle='                incbin "../Resources/17_ACTION/'+old_code.name+'"';assert text.count(needle)==1
    replacement='                incbin "../Resources/17_ACTION/'+code_prefix.rsplit('/',1)[-1]+'"\n'
    replacement+='                assert $ == #132A\n                disp #70ED\n                include "../Action/SelectMissileStock.asm"\n                ent\n'
    replacement+='                assert $ == #1333\n                ; Unknown, остальные обработчики ещё не разобраны\n                incbin "../Resources/17_ACTION/'+code_suffix.rsplit('/',1)[-1]+'"'
    text=text.replace(needle,replacement)
    old_data=next(p for p,(start,length) in previous.items() if start==0x3C12)
    needle='                incbin "../Resources/17_ACTION/'+old_data.name+'"';assert text.count(needle)==1
    replacement='                disp #9C12\n                include "../Action/Data/MissileStock.asm"\n                ent\n'
    replacement+='                assert $ == #3C14\n                ; Unknown, соседние данные ещё не разобраны\n                incbin "../Resources/17_ACTION/'+data_suffix.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionMissileStockFacts import FUNCTIONS as ACTION_MISSILE_STOCK_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_MISSILE_STOCK_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionMissileStockFacts import CONTRACTS as ACTION_MISSILE_STOCK_CONTRACTS\nCONTRACTS.update(ACTION_MISSILE_STOCK_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_missile_stock_name_operands(region,function_address,operation)')
    text+="\nfrom ActionMissileStockFacts import name_operands as action_missile_stock_name_operands\nDOCUMENTS['Action',0x70ED]=('ActionMissileStock','выбор остатка ракет')\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    hook='''    # Физическая пара байтов остатка ракет, Fallback перед Preferred.
    if "struct FMissileStock" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionMissileStockFacts import TABLE as MISSILE_STOCK, render as render_missile_stock
        text,bindings=render_missile_stock(data_by_slot[17])
        write(MISSILE_STOCK[1],text)
        symbols.update(bindings)
        special[17,0x3C12]=(0x3C14,MISSILE_STOCK[1],0x9C12)
'''
    assert text.count(needle)==1;text=text.replace(needle,hook+needle)
    needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    text=text.replace(needle,"\nfrom ActionMissileStockFacts import COMMENTS as ACTION_MISSILE_STOCK_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_STOCK_COMMENTS)\n"+needle)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    hook='''    # Проверка физической пары двух байтов остатка ракет и обратного порядка полей.
    from ActionMissileStockFacts import TABLE as MISSILE_STOCK, parse as parse_missile_stock
    missile_stock_records=0
    entries=[item for item in source_map if item['path']==MISSILE_STOCK[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_missile_stock((ROOT/MISSILE_STOCK[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3C12,2,0x9C12)
        assert raw==sources[17][0x3C12:0x3C14]
        assert all(symbols.get(key.upper())==value for key,value in labels.items())
        assert symbols['FMISSILESTOCK']==2 and symbols['FMISSILESTOCK.FALLBACK']==0 and symbols['FMISSILESTOCK.PREFERRED']==1
        missile_stock_records=1

'''
    assert text.count(needle)==1;text=text.replace(needle,hook+needle)
    needle="    report['key_scan_records'] = key_scan_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['missile_stock_records'] = missile_stock_records").encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions)
    described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #74FB |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #70ED | [Action.SelectMissileStock](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## SelectFuelStock\n';assert text.count(needle)==1
    section='## SelectMissileStock\n\n[Action.SelectMissileStock](../../'+code_path+')\n\n'+description+'.\n\nВход `#70ED`, запись 17, смещения `#132A..#1332`.\n\n[Назначение, контракт и проверка](../ActionMissileStock.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionMissileStock';history=ROOT/'Tools/Disasm/Research/History/BeforeActionMissileStock'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка отсутствия новых пользовательских изменений.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},**{p:p.read_bytes() for p in previous}}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только двух заменённых ресурсов после сверки с исходной копией.
    for path,(start,length) in previous.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes()==source[start:start+length]==(history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    report=dict(passed=True,typed_bytes=2,physical_records=1,confirmed_code_bytes=9,confirmed_instructions=7,
        described_functions=1,independent_model_cases=65536,physical_bytes_preserved=True,
        subtype_meaning_of_two_counters_proved=False,caller_handlers_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileStockClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
