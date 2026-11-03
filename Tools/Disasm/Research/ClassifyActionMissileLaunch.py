"""Публикация двух проверенных входов и трёх физических кодов захвата, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionMissileLaunchFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionMissileLaunchVerification');assert proof['passed'] and proof['total_cases']==80992
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    code_old=next(i for i in source_map if i['slot']==17 and i['offset']==0x1289)
    data_old=next(i for i in source_map if i['slot']==17 and i['offset']==0x3B19)
    assert (code_old['length'],code_old['kind'])==(0xA1,'unclassified')
    assert (data_old['length'],data_old['kind'])==(0x68,'unclassified')
    previous={ROOT/i['path']:(i['offset'],i['length']) for i in (code_old,data_old)}
    for path,(start,length) in previous.items():assert path.read_bytes()==source[start:start+length]
    code_prefix='Source/Resources/17_ACTION/Unclassified017_BeforeMissileChecks.bin'
    code_suffix='Source/Resources/17_ACTION/Unclassified017_AfterMissileChecks.bin'
    data_prefix='Source/Resources/17_ACTION/Unclassified020_BeforeMissileTargets.bin'
    data_suffix='Source/Resources/17_ACTION/Unclassified020_AfterMissileTargets.bin'
    data_text,bindings=facts.render(source);assert facts.parse(data_text)==(source[0x3B1B:0x3B1E],bindings)
    assert not any(k in symbols for k in bindings);symbols.update(bindings)
    pending={ROOT/facts.TABLE[1]:data_text.encode('utf-8'),ROOT/code_prefix:source[0x1289:0x12D8],
        ROOT/code_suffix:source[0x1303:0x132A],ROOT/data_prefix:source[0x3B19:0x3B1B],ROOT/data_suffix:source[0x3B1E:0x3B81]}
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    index=source_map.index(code_old)
    source_map[index:index+1]=[piece(0x1289,0x12D8,'unclassified',code_prefix,None),
        piece(0x12D8,0x12E1,'code','Source/Action/ReportMissingMissileTarget.asm',0x709B),
        piece(0x12E1,0x1303,'code','Source/Action/CheckMissileLaunch.asm',0x70A4),piece(0x1303,0x132A,'unclassified',code_suffix,None)]
    index=source_map.index(data_old)
    source_map[index:index+1]=[piece(0x3B19,0x3B1B,'unclassified',data_prefix,None),
        piece(0x3B1B,0x3B1E,'typed_data',facts.TABLE[1],0x9B1B),piece(0x3B1E,0x3B81,'unclassified',data_suffix,None)]
    instructions=decoder(flat_action()).disassemble(0x709B,0x70C6,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000+0x23D) for i in instructions]
    assert len(records)==22 and b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x12D8:0x1303]
    region=next(r for r in flow if r['name']=='Action')
    assert not any(0x709B<=i['address']<0x70C6 for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS))
    region['calls']=sorted(set(region['calls'])|{0x6040,0x70ED});region['branches']=sorted(set(region['branches'])|{0x709B})
    region['instruction_count']+=22;region['code_bytes']+=43;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    for address,(name,description) in facts.FUNCTIONS.items():
        key='Action.'+name+'.Entry';assert key not in symbols;symbols[key]=address
    for address,end in ((0x709B,0x70A4),(0x70A4,0x70C6)):
        name,description=facts.FUNCTIONS[address];path_string='Source/Action/'+name+'.asm'
        function=dict(region='Action',name=name,address=address,slot=17,offset=address-0x6000+0x23D,
            description=description,semantic_status='described',end_offset=end-0x6000+0x23D,path=path_string)
        index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']==0x70ED)
        functions.insert(index,function)
        lines=['                module Action','                module '+name,
            '                ; Документация [проверка перед пуском](../../Docs/ActionMissileLaunch.md)',
            '                ; -----------------------------------------','                ; '+description,
            '                ; исходная запись 17, перенесённый код банка 5, адреса '+format(address,'04X')+'..'+format(end-1,'04X')]
        for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',address]):
            lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
        lines+=['                ; -----------------------------------------']
        for record in records:
            pc=record['address']
            if not address<=pc<end:continue
            before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
            op=facts.name_operands('Action',address,record['operation'].replace(',',', '))
            line=('Entry:          ' if pc==address else ' '*16)+op
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        lines+=['                endmodule','                endmodule']
        pending[ROOT/path_string]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+22)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FMissileTargets' not in text
    block='\n                ; Три физических кода захваченных целей ракет\n                struct FMissileTargets\n'
    for field,width,note in facts.FIELDS:block+=field.ljust(16)+('db #00').ljust(64)+'; '+note+'\n'
    block+='                ends\n                assert FMissileTargets == 3\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionMissileLaunchState' not in text
    block='\n                ; Существующий операнд задержки команд, память не выделяется\n                module ActionMissileLaunchState\n'
    for field,address,note in facts.STATE_FIELDS:block+=field.ljust(16)+('equ #'+format(address,'04X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionMissileLaunchConst' not in text
    block='\n                ; Константы проверки ракет, указатели сообщений относятся к Controls банка 1\n                module ActionMissileLaunchConst\n'
    for field,value,note in (('NoTarget',0xFF,'код отсутствия захвата'),('DelayTicks',5,'положительное значение, уменьшаемое UpdateFrame'),
                            ('NoTargetText',0xF2C5,'указатель сообщения об отсутствии захваченной цели, банк 1'),('EmptyStockText',0xF280,'указатель сообщения об исчерпанных ракетах, банк 1')):
        block+=field.ljust(16)+('equ #'+format(value,'04X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    old_code=next(p for p,(start,length) in previous.items() if start==0x1289)
    needle='                incbin "../Resources/17_ACTION/'+old_code.name+'"';assert text.count(needle)==1
    replacement='                incbin "../Resources/17_ACTION/'+code_prefix.rsplit('/',1)[-1]+'"\n'
    for start,origin,name in ((0x12D8,0x709B,'ReportMissingMissileTarget'),(0x12E1,0x70A4,'CheckMissileLaunch')):
        replacement+='                assert $ == #'+format(start,'04X')+'\n                disp #'+format(origin,'04X')+'\n'
        replacement+='                include "../Action/'+name+'.asm"\n                ent\n'
    replacement+='                assert $ == #1303\n                ; Unknown, хвост пуска ещё не разобран\n                incbin "../Resources/17_ACTION/'+code_suffix.rsplit('/',1)[-1]+'"'
    text=text.replace(needle,replacement)
    old_data=next(p for p,(start,length) in previous.items() if start==0x3B19)
    needle='                incbin "../Resources/17_ACTION/'+old_data.name+'"';assert text.count(needle)==1
    replacement='                incbin "../Resources/17_ACTION/'+data_prefix.rsplit('/',1)[-1]+'"\n'
    replacement+='                assert $ == #3B1B\n                disp #9B1B\n                include "../Action/Data/MissileTargets.asm"\n                ent\n'
    replacement+='                assert $ == #3B1E\n                ; Unknown, соседние данные ещё не разобраны\n                incbin "../Resources/17_ACTION/'+data_suffix.rsplit('/',1)[-1]+'"'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionMissileLaunchFacts import FUNCTIONS as ACTION_MISSILE_LAUNCH_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_MISSILE_LAUNCH_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionMissileLaunchFacts import CONTRACTS as ACTION_MISSILE_LAUNCH_CONTRACTS\nCONTRACTS.update(ACTION_MISSILE_LAUNCH_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle)==1;text=text.replace(needle,needle+'\n    operation = action_missile_launch_name_operands(region,function_address,operation)')
    text+="\nfrom ActionMissileLaunchFacts import name_operands as action_missile_launch_name_operands\nDOCUMENTS.update({('Action',a):('ActionMissileLaunch','проверка перед пуском') for a in (0x709B,0x70A4)})\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    token_text, token_records = render_token_tables(language, names)'
    hook='''    # Физические коды трёх захваченных целей ракет.
    if "struct FMissileTargets" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionMissileLaunchFacts import TABLE as MISSILE_TARGETS, render as render_missile_targets
        text,bindings=render_missile_targets(data_by_slot[17])
        write(MISSILE_TARGETS[1],text)
        symbols.update(bindings)
        special[17,0x3B1B]=(0x3B1E,MISSILE_TARGETS[1],0x9B1B)
'''
    assert text.count(needle)==1;text=text.replace(needle,hook+needle);needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionMissileLaunchFacts import COMMENTS as ACTION_MISSILE_LAUNCH_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_LAUNCH_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.'
    hook='''    # Проверка трёх физических кодов захвата, исходные значения не заменяются.
    from ActionMissileLaunchFacts import TABLE as MISSILE_TARGETS, parse as parse_missile_targets
    missile_target_records=0
    entries=[item for item in source_map if item['path']==MISSILE_TARGETS[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_missile_targets((ROOT/MISSILE_TARGETS[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3B1B,3,0x9B1B)
        assert raw==sources[17][0x3B1B:0x3B1E]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FMISSILETARGETS']==3
        assert [symbols['FMISSILETARGETS.TARGET'+str(i)] for i in range(3)]==[0,1,2]
        missile_target_records=1

'''
    assert text.count(needle)==1;text=text.replace(needle,hook+needle);needle="    report['missile_stock_records'] = missile_stock_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['missile_target_records'] = missile_target_records").encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions)
    described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #70ED |';assert text.count(needle)==1
    newrows=''.join('| #'+format(a,'04X')+' | [Action.'+n+'](../Source/Action/'+n+'.asm) | '+d+' |\n' for a,(n,d) in facts.FUNCTIONS.items())
    pending[path]=text.replace(needle,newrows+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## SelectMissileStock\n';assert text.count(needle)==1
    sections=''.join('## '+n+'\n\n[Action.'+n+'](../../Source/Action/'+n+'.asm)\n\n'+d+'.\n\nВход `#'+format(a,'04X')+'`, запись 17.\n\n[Контракт и композиционная проверка](../ActionMissileLaunch.md).\n\n' for a,(n,d) in facts.FUNCTIONS.items())
    pending[path]=text.replace(needle,sections+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionMissileLaunch';history=ROOT/'Tools/Disasm/Research/History/BeforeActionMissileLaunch'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и сверка рабочей копии до записи активных файлов.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},**{p:p.read_bytes() for p in previous}}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление двух заменённых ресурсов после сохранения и проверки их исходных копий.
    for path,(start,length) in previous.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes()==source[start:start+length]==(history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    report=dict(passed=True,described_functions=2,confirmed_code_bytes=43,confirmed_instructions=22,
        typed_bytes=3,physical_records=1,compositional_model_cases=proof['total_cases'],
        independent_complete_child_oracle=False,cases_by_entry={'709B':9216,'70A4':71776},
        physical_bytes_preserved=True,missile_launch_itself_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileLaunchClassification.json').write_bytes(encode(report))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
