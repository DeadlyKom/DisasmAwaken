"""Публикация всех трёх проверенных путей 60AE с реальными полями FActionRecord, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionMissileCreationFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    created,lost=read('ActionMissileCreationVerification'),read('ActionLostMissileTargetVerification')
    assert created['passed'] and lost['passed'] and (created['total_cases'],lost['total_cases'])==(12263,36864)
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x2EB)
    assert (old['length'],old['kind'])==(151,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x2EB:0x382]
    name,description=facts.FUNCTIONS[0x60AE];code_path='Source/Action/'+name+'.asm'
    source_map[source_map.index(old)]=dict(slot=17,offset=0x2EB,length=151,kind='code',path=code_path,origin=0x60AE,
        sha256=hashlib.sha256(source[0x2EB:0x382]).hexdigest())
    instructions=decoder(flat_action()).disassemble(0x60AE,0x6145,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000+0x23D) for i in instructions]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x2EB:0x382]
    region=next(r for r in flow if r['name']=='Action');assert not any(0x60AE<=i['address']<0x6145 for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0x60AE});region['calls']=sorted(set(region['calls'])|{0xE6A7,0x6040,0xACEA,0x70ED,0xE9A1,0xE6BE})
    region['branches']=sorted(set(region['branches'])|{0x60C8,0x60E6});region['instruction_count']+=len(records);region['code_bytes']+=151
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    validate_notes([region],{'Action':facts.COMMENTS})
    for address,label in ((0x60AE,'Entry'),*facts.LOCAL.items()):
        key='Action.'+name+'.'+label;assert key not in symbols;symbols[key]=address
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>0x60AE)
    functions.insert(index,dict(region='Action',name=name,address=0x60AE,slot=17,offset=0x2EB,
        description=description,semantic_status='described',end_offset=0x382,path=code_path))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/('Tools/Disasm/Reports/'+stem+'.json'):encode(value) for stem,value in
        (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow))}
    modified=read('ModifiedCode')
    for writer,target,target_instruction,size,operation in ((0x60BB,0xECA9,0xECA8,2,'LD HL,#0000'),
        (0x60E8,0x612E,0x612B,1,'LD (IY+#13),#00')):
        assert not any(i['region']=='Action' and i['writer']==writer for i in modified)
        modified.append(dict(region='Action',writer=writer,target=target,target_instruction=target_instruction,size=size,
            target_operation=operation,path=code_path))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
    lines=['                module Action','                module '+name,
        '                ; Документация [создание записи ракеты](../../Docs/ActionMissileCreation.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, перенесённое ядро банка 5, адреса 60AE..6144']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0x60AE]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0x60AE,record['operation'].replace(',',', '));label='Entry' if pc==0x60AE else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionMissileCreateState' not in text
    block='\n                ; Существующий непосредственный байт инициализации Unknown13\n                module ActionMissileCreateState\n'
    block+='InitParameter   equ #612E'.ljust(80)+'; четвёртый байт LD (IY+d),n, память не выделяется\n                endmodule\n'
    block+='\n                ; Исходный операнд AY-потребителя ACTION банка 0\n                module ActionAyEffectState\n'
    block+='CursorA         equ #ECA9'.ljust(80)+'; операнд LD HL,nn по ECA8, поток канала A, не Controls банка 1\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionMissileCreateConst' not in text
    block='\n                ; Подтверждённые значения создания записи ракеты\n                module ActionMissileCreateConst\n'
    for label,value,note in (('ActionSound',0xEDA8,'поток канала A в ACTION банка 0'),('LostText',0xF248,'сообщение о потерянной цели, Controls банка 1'),
        ('InitialComp2',400,'третье входное слово, единицы ещё неизвестны'),('FallbackParam',10,'Unknown13 при поле Fallback'),
        ('PreferredParam',50,'Unknown13 при поле Preferred'),('MissileClass',0x11,'ClassCode создаваемой записи')):
        block+=label.ljust(16)+('equ #'+format(value,'04X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    pending[path]=text.replace(needle,'                disp #60AE\n                include "../Action/'+name+'.asm"\n                ent').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionMissileCreationFacts import FUNCTIONS as ACTION_MISSILE_CREATION_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_MISSILE_CREATION_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionMissileCreationFacts import CONTRACTS as ACTION_MISSILE_CREATION_CONTRACTS\nCONTRACTS.update(ACTION_MISSILE_CREATION_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_missile_creation_name_operands(region,function_address,operation)')
    text+="\nfrom ActionMissileCreationFacts import name_operands as action_missile_creation_name_operands\nDOCUMENTS['Action',0x60AE]=('ActionMissileCreation','создание записи ракеты')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionMissileCreationFacts import COMMENTS as ACTION_MISSILE_CREATION_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_CREATION_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);following=functions[index+1];needle='| #'+format(following['address'],'04X')+' |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #60AE | [Action.'+name+'](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Три пути, поля, флаги и модели](../ActionMissileCreation.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');heading='## Параметр записи и звук в 60AE';assert heading not in text
    text+='\n'+heading+'\n\n[CreateMissileForTarget](../Source/Action/CreateMissileForTarget.asm) записывает слово потока канала A, 60BB→ECA9 в банке 0, и байт параметра, 60E8→612E. Последний является непосредственным байтом LD (IY+Unknown13),n. [Три пути и банковый контекст](ActionMissileCreation.md) описаны отдельно.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionMissileCreation';history=ROOT/'Tools/Disasm/Research/History/BeforeActionMissileCreation';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка отсутствия новых пользовательских изменений перед публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого ресурса после проверки и сохранения исходных байтов.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x2EB:0x382]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,confirmed_code_bytes=151,confirmed_instructions=len(records),
        compositional_model_cases=49127,independent_complete_child_oracle=False,physical_bytes_preserved=True,
        actual_ay_bank0_and_text_bank1_distinguished=True,all_three_paths_checked=True,
        maximum_additional_stack_bytes=18,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileCreationClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
