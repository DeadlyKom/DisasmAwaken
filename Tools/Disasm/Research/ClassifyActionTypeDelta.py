"""Выделение общего хвоста 6380 и шестнадцати исходных поправок, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
import ActionTypeDeltaFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionTypeDeltaVerification');assert proof['passed'] and proof['total_cases']==90112
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    parent=next(f for f in functions if f['region']=='Action' and f['address']==0x635B)
    assert parent['semantic_status']=='unknown' and parent['end_offset']==0x5F3
    code_old=next(i for i in source_map if i['path']==parent['path'])
    raw_old=next(i for i in source_map if i['slot']==17 and i['offset']==0x54E)
    assert raw_old['length']==74 and (ROOT/raw_old['path']).read_bytes()==source[0x54E:0x598]
    pending={};old_path=ROOT/raw_old['path'];raw_prefix='Source/Resources/17_ACTION/Unclassified005_BeforeTypeDeltas.bin'
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    name,description=facts.FUNCTIONS[0x6380];code_path='Source/Action/'+name+'.asm'
    index=source_map.index(code_old);source_map[index:index+1]=[
        piece(0x598,0x5BD,'code',parent['path'],0x635B),piece(0x5BD,0x5F3,'code',code_path,0x6380)]
    index=source_map.index(raw_old);source_map[index:index+1]=[
        piece(0x54E,0x588,'unclassified',raw_prefix,None),piece(0x588,0x598,'typed_data',facts.TABLE[1],0x634B)]
    parent['end_offset']=0x5BD
    functions.insert(functions.index(parent)+1,dict(region='Action',name=name,address=0x6380,slot=17,offset=0x5BD,
        description=description,semantic_status='described',end_offset=0x5F3,path=code_path))
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if 0x6380<=i['address']<0x63B6]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x5BD:0x5F3]
    region['roots']=sorted(set(region['roots'])|{0x6380})
    renames={'Action.Unknown635B.Point'+format(a,'04X'):'Action.'+name+'.'+label for a,label in facts.LOCAL.items()}
    for before,after in renames.items():assert after not in symbols;symbols[after]=symbols.pop(before)
    assert 'Action.'+name+'.Entry' not in symbols;symbols['Action.'+name+'.Entry']=0x6380
    text,bindings=facts.render(source);assert facts.parse(text)==(source[0x588:0x598],bindings)
    assert not any(k in symbols for k in bindings);symbols.update(bindings);pending[ROOT/facts.TABLE[1]]=text.encode('utf-8')
    pending[ROOT/raw_prefix]=source[0x54E:0x588]
    path=ROOT/parent['path'];text=path.read_text('utf-8');needle='                LD A, B\n                CP #10\n'
    assert text.count(needle)==1
    prefix=text[:text.index(needle)].replace('#0598..#05F2','#0598..#05BC')
    prefix=prefix.replace('Entry:','                ; (0) Жёсткий порядок, продолжение в ApplyIndexedDelta.asm\nEntry:',1)
    pending[path]=(prefix+'                ; JP @Action.ApplyIndexedDelta.Entry, продолжение в ApplyIndexedDelta.asm\n\n                endmodule\n                endmodule\n').encode('utf-8')
    lines=['                module Action','                module '+name,
        '                ; (1) Жёсткий порядок, общий хвост после Unknown635B.asm',
        '                ; Документация [табличная поправка](../../Docs/ActionTypeDelta.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, перенесённый код банка 5, адреса 6380..63B5']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x6380]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0x6380,record['operation'].replace(',',', '))
        label='Entry' if pc==0x6380 else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FIndexedDelta' not in text
    block='\n                ; Физическая знаковая поправка исходной таблицы\n                struct FIndexedDelta\n'
    block+='Delta:          db #00'.ljust(80)+'; signed8, отрицательные значения не получают добавку режима\n'
    block+='                ends\n                assert FIndexedDelta == 1\n\n'
    # Проверка принятого в STRUCT синтаксиса полей, двоеточие не требуется для объявления.
    block=block.replace('Delta:          db','Delta           db')
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    repl='                incbin "../Resources/17_ACTION/'+raw_prefix.rsplit('/',1)[-1]+'"\n                assert $ == #0588\n                disp #634B\n                include "../Action/Data/TypeDeltas.asm"\n                ent\n                assert $ == #0598'
    text=text.replace(needle,repl);needle='                include "../Action/Unknown635B.asm"';assert text.count(needle)==1
    text=text.replace(needle,needle.ljust(80)+'; (0) жёсткий порядок, последовательное исполнение\n'+
        '                include "../Action/ApplyIndexedDelta.asm"'.ljust(80)+'; (1) жёсткий порядок, продолжение после условного RET Z')
    pending[path]=text.encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionTypeDeltaFacts import FUNCTIONS as ACTION_TYPE_DELTA_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_TYPE_DELTA_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionTypeDeltaFacts import CONTRACTS as ACTION_TYPE_DELTA_CONTRACTS\nCONTRACTS.update(ACTION_TYPE_DELTA_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_type_delta_name_operands(region,function_address,operation)')
    text+="\nfrom ActionTypeDeltaFacts import name_operands as action_type_delta_name_operands\nDOCUMENTS['Action',0x6380]=('ActionTypeDelta','табличная поправка')\n"
    text+='LABELS.update('+repr({('Action',a):'Action.ApplyIndexedDelta.'+label for a,label in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические знаковые поправки перенесённого ядра ACTION.
    if "struct FIndexedDelta" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionTypeDeltaFacts import TABLE as TYPE_DELTAS, render as render_type_deltas
        text,bindings=render_type_deltas(data_by_slot[17])
        write(TYPE_DELTAS[1],text)
        symbols.update(bindings)
        special[17,0x588]=(0x598,TYPE_DELTAS[1],0x634B)
'''
    text=text.replace(needle,hook+needle);needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionTypeDeltaFacts import COMMENTS as ACTION_TYPE_DELTA_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_TYPE_DELTA_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.';assert text.count(needle)==1
    hook='''    # Проверка шестнадцати знаковых поправок и исходного физического смещения.
    from ActionTypeDeltaFacts import TABLE as TYPE_DELTAS, parse as parse_type_deltas
    type_delta_records=0
    entries=[i for i in source_map if i['path']==TYPE_DELTAS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_type_deltas((ROOT/TYPE_DELTAS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x588,16,0x634B)
        assert raw==sources[17][0x588:0x598]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FINDEXEDDELTA']==1 and symbols['FINDEXEDDELTA.DELTA']==0
        type_delta_records=16

'''
    text=text.replace(needle,hook+needle);needle="    report['missile_target_records'] = missile_target_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['type_delta_records'] = type_delta_records").encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');needle='| #635B |';start=text.index(needle);end=text.index('\n',start)+1
    row='| #6380 | [Action.'+name+'](../'+code_path+') | '+description+' |\n';text=text[:end]+row+text[end:]
    total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    pending[path]=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');start=text.index('## Unknown635B\n');end=text.find('\n## ',start+4);assert end>0
    section='\n## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Договор и независимая модель](../ActionTypeDelta.md).\n'
    pending[path]=(text[:end]+section+text[end:]).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionTypeDelta';history=ROOT/'Tools/Disasm/Research/History/BeforeActionTypeDelta';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка отсутствия новых правок до записи активных файлов.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого ресурса после сверки и сохранения исходной копии.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x54E:0x598]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,split_from_unknown=True,parent_unknown_preserved=True,
        typed_bytes=16,physical_records=16,independent_model_cases=90112,physical_bytes_preserved=True,
        original_instruction_sequence_preserved=True,game_meaning_of_state_and_mode_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionTypeDeltaClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
