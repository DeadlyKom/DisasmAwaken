"""Однократное выделение проверенного хвоста 70C6, без ассемблера и сборочных генераторов."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionMissileConsumeFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionMissileConsumeVerification');assert proof['passed'] and proof['total_cases']==71040
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x1303)
    assert (old['length'],old['kind'])==(39,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x1303:0x132A]
    name,description=facts.FUNCTIONS[0x70C6];code_path='Source/Action/'+name+'.asm'
    source_map[source_map.index(old)]=dict(slot=17,offset=0x1303,length=39,kind='code',path=code_path,origin=0x70C6,
        sha256=hashlib.sha256(source[0x1303:0x132A]).hexdigest())
    instructions=decoder(flat_action()).disassemble(0x70C6,0x70ED,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000+0x23D) for i in instructions]
    assert len(records)==19 and b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x1303:0x132A]
    region=next(r for r in flow if r['name']=='Action')
    assert not any(0x70C6<=i['address']<0x70ED for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0x70C6});region['calls']=sorted(set(region['calls'])|{0x6000,0x6040,0x70ED})
    region['instruction_count']+=19;region['code_bytes']+=39;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    key='Action.'+name+'.Entry';assert key not in symbols;symbols[key]=0x70C6
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']==0x70ED)
    functions.insert(index,dict(region='Action',name=name,address=0x70C6,slot=17,offset=0x1303,
        description=description,semantic_status='described',end_offset=0x132A,path=code_path))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+19)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/('Tools/Disasm/Reports/'+stem+'.json'):encode(value) for stem,value in
        (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow))}
    lines=['                module Action','                module '+name,
        '                ; Документация [списание ракет](../../Docs/ActionMissileConsume.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, перенесённый код банка 5, адреса 70C6..70EC']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x70C6]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0x70C6,record['operation'].replace(',',', '))
        line=('Entry:          ' if pc==0x70C6 else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule']
    pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionMissileConsumeConst' not in text
    block='\n                ; Адреса текстов списания ракеты, Controls банка 1\n                module ActionMissileConsumeConst\n'
    for field,address,note in (('LaunchedText',0xF2E9,'сообщение о пуске'),('RemainingText',0xF26D,'начало фразы остатка'),('MissilesText',0xF277,'конец фразы остатка')):
        block+=field.ljust(16)+('equ #'+format(address,'04X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                ; Unknown, хвост пуска ещё не разобран\n                incbin "../Resources/17_ACTION/'+old_path.name+'"'
    assert text.count(needle)==1
    replacement='                disp #70C6\n                include "../Action/'+name+'.asm"\n                ent\n                assert $ == #132A'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionMissileConsumeFacts import FUNCTIONS as ACTION_MISSILE_CONSUME_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_MISSILE_CONSUME_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionMissileConsumeFacts import CONTRACTS as ACTION_MISSILE_CONSUME_CONTRACTS\nCONTRACTS.update(ACTION_MISSILE_CONSUME_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)'
    assert text.count(needle)==1;text=text.replace(needle,needle+'\n    operation = action_missile_consume_name_operands(region,function_address,operation)')
    text+="\nfrom ActionMissileConsumeFacts import name_operands as action_missile_consume_name_operands\nDOCUMENTS['Action',0x70C6]=('ActionMissileConsume','списание ракет')\n";pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionMissileConsumeFacts import COMMENTS as ACTION_MISSILE_CONSUME_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_CONSUME_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions)
    described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);needle='| #70ED |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #70C6 | [Action.'+name+'](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## SelectMissileStock\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\nВход `#70C6`, запись 17.\n\n[Контракт и композиционная проверка](../ActionMissileConsume.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionMissileConsume';history=ROOT/'Tools/Disasm/Research/History/BeforeActionMissileConsume'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка рабочей копии перед заменой.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление единственного заменённого ресурса после проверки и сохранения оригинала.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x1303:0x132A]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,confirmed_code_bytes=39,confirmed_instructions=19,
        compositional_model_cases=71040,independent_complete_child_oracle=False,physical_bytes_preserved=True,
        auxiliary_counter_game_meaning_proved=False,rocket_object_creation_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileConsumeClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
