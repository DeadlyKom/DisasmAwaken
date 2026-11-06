"""Точечная публикация 79 исходных байтов запросов ракет, только после функциональной модели."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from CheckActionParameterActivation import flat_action
import ActionMissileRequestsFacts as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionMissileRequestsVerification');assert proof['passed'] and proof['total_cases']==16372
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x1289)
    assert old['length']==79 and old['kind']=='unclassified';old_path=ROOT/old['path']
    assert old_path.read_bytes()==source[0x1289:0x12D8]
    instructions=decoder(flat_action()).disassemble(0x704C,0x709B,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000+0x23D) for i in instructions]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x1289:0x12D8]
    region=next(r for r in flow if r['name']=='Action');assert not any(0x704C<=i['address']<0x709B for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS));region['branches']=sorted(set(region['branches'])|{0x705D})
    region['calls']=sorted(set(region['calls'])|{0x70A4,0x60AE,0x6380,0x70ED})
    region['instruction_count']+=len(records);region['code_bytes']+=79;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    validate_notes([region],{'Action':facts.COMMENTS});pending={};new_ranges=[];new_functions=[]
    for address,(name,description) in facts.FUNCTIONS.items():
        end=facts.ENDS[address];offset=address-0x6000+0x23D;end_offset=end-0x6000+0x23D;path='Source/Action/'+name+'.asm'
        new_ranges.append(dict(slot=17,offset=offset,length=end-address,kind='code',path=path,origin=address,
            sha256=hashlib.sha256(source[offset:end_offset]).hexdigest()))
        function=dict(region='Action',name=name,address=address,slot=17,offset=offset,description=description,
            semantic_status='described',end_offset=end_offset,path=path);new_functions.append(function)
        key='Action.'+name+'.Entry';assert key not in symbols;symbols[key]=address
        lines=['                module Action','                module '+name,
            '                ; Документация [запросы запуска ракет](../../Docs/ActionMissileRequests.md)',
            '                ; -----------------------------------------','                ; '+description,
            '                ; исходная запись 17, перенесённое ядро банка 5, адреса '+format(address,'04X')+'..'+format(end-1,'04X')]
        for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',address]):
            lines+=['                ; '+heading+':']+['                ;   '+value for value in values]
        lines+=['                ; -----------------------------------------']
        for record in records:
            if not address<=record['address']<end:continue
            before,right=facts.COMMENTS.get(record['address'],([],None));lines+=['                ; '+value for value in before]
            op=facts.name_operands('Action',address,record['operation'].replace(',',', '))
            line=('Entry:'.ljust(16) if record['address']==address else ' '*16)+op
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        lines+=['                endmodule','                endmodule']
        continuation=dict(region='Action',name='CompleteMissileLaunch',path='Source/Action/CompleteMissileLaunch.asm') if address==0x704C else None
        pending[ROOT/path]=format_function('\n'.join(lines)+'\n',continuation).encode('utf-8')
    index=source_map.index(old);source_map[index:index+1]=new_ranges
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>0x704C)
    following=functions[index];functions[index:index]=new_functions
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    modified=read('ModifiedCode');assert not any(i['region']=='Action' and i['writer']==0x7060 for i in modified)
    modified.append(dict(region='Action',writer=0x7060,target=0xECA9,target_instruction=0xECA8,size=2,
        target_operation='LD HL,#0000',path='Source/Action/CompleteMissileLaunch.asm'))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    includes=['                disp #704C']
    for number,function in enumerate(new_functions):
        line='                include "../Action/'+function['name']+'.asm"'
        if number<2:line=line.ljust(80)+'; ('+str(number)+') жёсткий порядок продолжения RequestMissile0'
        includes.append(line)
    includes.append('                ent');pending[path]=text.replace(needle,'\n'.join(includes)).encode('utf-8')
    # Обновление трёх реальных полей Target существующей таблицы, порядок и физические слова сохраняются.
    path=ROOT/'Source/Action/Data/KeyHandlerPointers.asm';text=path.read_text('utf-8')
    for address in (0x704C,0x7075,0x7088):
        needle='#'+format(address,'04X');assert text.count(needle)==1
        lines=[]
        for line in text.splitlines():
            if needle in line:
                line=('                    @Action.'+facts.FUNCTIONS[address][0]+'.Entry').ljust(80)+'; Target, условный запрос по соответствующему захвату'
            lines.append(line)
        text='\n'.join(lines)+'\n'
    pending[path]=text.encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionMissileRequestsFacts import FUNCTIONS as ACTION_MISSILE_REQUESTS_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_MISSILE_REQUESTS_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionMissileRequestsFacts import CONTRACTS as ACTION_MISSILE_REQUESTS_CONTRACTS\nCONTRACTS.update(ACTION_MISSILE_REQUESTS_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_missile_requests_name_operands(region,function_address,operation)')
    text+="\nfrom ActionMissileRequestsFacts import name_operands as action_missile_requests_name_operands\n"
    for address in facts.FUNCTIONS:text+=f"DOCUMENTS['Action',{address}]=('ActionMissileRequests','запросы запуска ракет')\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionMissileRequestsFacts import COMMENTS as ACTION_MISSILE_REQUESTS_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_MISSILE_REQUESTS_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);needle='| #'+format(following['address'],'04X')+' |';assert text.count(needle)==1
    rows=''.join('| #'+format(f['address'],'04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n' for f in new_functions)
    pending[path]=text.replace(needle,rows+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    sections=''.join('## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Пути, состояние и границы проверки](../ActionMissileRequests.md).\n\n' for f in new_functions)
    pending[path]=text.replace(needle,sections+needle).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');text+='\n## Общий хвост запуска ракет\n\n[CompleteMissileLaunch](../Source/Action/CompleteMissileLaunch.asm) записывает слово потока AY-канала A, 7060→ECA9 в банке 0. При потерянной цели CreateMissileForTarget повторяет ту же запись. [Порядок и отказы](ActionMissileRequests.md) описаны отдельно.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionMissileRequests';history=ROOT/'Tools/Disasm/Research/History/BeforeActionMissileRequests'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Сохранение отдельного кандидата и истории до изменения исходников, с проверкой текущей рабочей копии.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только точно заменённого бинарного фрагмента, оригинальные байты сохранены в образе и истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x1289:0x12D8]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=4,confirmed_code_bytes=79,confirmed_instructions=len(records),
        compositional_model_cases=proof['total_cases'],independent_complete_child_oracle=False,
        physical_bytes_preserved=True,target_class_field_proved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileRequestsClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
