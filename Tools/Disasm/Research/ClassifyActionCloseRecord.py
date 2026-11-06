"""Публикация трёх проверенных входов E506..E55B, включая общий хвост и дополнительный вход."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from CheckActionParameterActivation import flat_action
import ActionCloseRecordFacts as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionCloseRecordVerification');assert proof['passed'] and proof['total_cases']==93184
    for tag in ('ActionVectorReverse','ActionStationTransfer'):assert read(tag+'Classification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    functions,source_map,symbols,inventory,flow,modified=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x8506)
    assert (old['length'],old['kind'])==(86,'unclassified');old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x8506:0x855C]
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000)
        for i in decoder(flat_action()).disassemble(0xE506,0xE55C,'h')]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x8506:0x855C]
    region=next(r for r in flow if r['name']=='Action');assert not any(0xE506<=i['address']<0xE55C for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS));region['calls']=sorted(set(region['calls'])|{0x6EDE})
    region['branches']=sorted(set(region['branches'])|{0x6CE4,0xE54A,*facts.LOCAL})
    region['instruction_count']+=len(records);region['code_bytes']+=86;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    validate_notes([region],{'Action':facts.COMMENTS});pending={};new_functions=[];ranges=[];control_names={}
    for address,(name,description) in facts.FUNCTIONS.items():
        end=facts.ENDS[address];path='Source/Action/'+name+'.asm'
        f=dict(region='Action',name=name,address=address,slot=17,offset=address-0x6000,end_offset=end-0x6000,path=path,description=description,semantic_status='described')
        new_functions.append(f);ranges.append(dict(old,offset=f['offset'],length=end-address,path=path,kind='code',origin=address,
            sha256=hashlib.sha256(source[f['offset']:f['end_offset']]).hexdigest()))
        control_names[address]='Action.'+name+'.Entry'
        for pc,label in ((address,'Entry'),*((pc,label) for pc,label in facts.LOCAL.items() if address<=pc<end)):
            key='Action.'+name+'.'+label;assert key not in symbols;symbols[key]=pc;control_names[pc]=key
    for f in new_functions:
        address,end=f['address'],f['end_offset']+0x6000
        lines=['                module Action','                module '+f['name'],
            '                ; Документация [три входа обработки записи](../../Docs/ActionCloseRecord.md)',
            '                ; -----------------------------------------','                ; '+f['description'],
            '                ; исходная запись 17, код ACTION банка 0, адреса '+format(address,'04X')+'..'+format(end-1,'04X')]
        for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',address]):
            lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
        lines.append('                ; -----------------------------------------')
        for record in records:
            pc=record['address']
            if not address<=pc<end:continue
            before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
            op=record['operation'].replace(',',', ')
            if op.startswith(('JP ','JR ','CALL ')):
                for target,target_name in control_names.items():op=op.replace('#'+format(target,'04X'),'@'+target_name)
            op=facts.name_operands('Action',address,op);label='Entry' if pc==address else facts.LOCAL.get(pc,'')
            assert len(label)<=15;line=((label+':').ljust(16) if label else ' '*16)+op
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        lines+=['                endmodule','                endmodule']
        continuation=new_functions[2] if address==0xE51F else None
        pending[ROOT/f['path']]=format_function('\n'.join(lines)+'\n',continuation).encode('utf-8')
    index=functions.index(next(f for f in functions if f['region']=='Action' and f['address']>0xE506));following=functions[index]
    functions[index:index]=new_functions;index=source_map.index(old);source_map[index:index+1]=ranges
    # Регистрация косвенного DEC и всех уже видимых прямых писателей раскрытого операнда InhibitCode.
    inhibit_writers=[]
    for i in region['instructions']:
        if i['address']==0xE54D or i['operation']=='LD (#E507),A':
            owner=next(f for f in functions if f['region']=='Action' and f['address']<=i['address']<f['address']+f['end_offset']-f['offset'])
            if not any(m['region']=='Action' and m['writer']==i['address'] and m['target']==0xE507 for m in modified):
                modified.append(dict(region='Action',writer=i['address'],target=0xE507,target_instruction=0xE506,size=1,
                    target_operation='LD A,#00',path=owner['path']))
            inhibit_writers.append((i['address'],owner['path']))
    assert any(pc==0xE54D for pc,_ in inhibit_writers)
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    # Именование входящего условного вызова и двух прямых обращений уже существующего кадра без переоформления остального кода.
    for path in (ROOT/'Source/Action').glob('*.asm'):
        text=path.read_text('utf-8');after=[];changed=False
        for line in text.splitlines():
            if 'CALL P, #E506' in line or '(#E507)' in line:
                code,separator,comment=line.partition(';')
                code=code.replace('CALL P, #E506','CALL P, @Action.DispatchCloseRecord.Entry').replace('(#E507)','(@ActionCloseRecordState.InhibitCode)')
                line=code.rstrip().ljust(80)+';'+comment if separator else code.rstrip();changed=True
            after.append(line)
        if changed:pending[path]=('\n'.join(after)+'\n').encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionCloseRecordState' not in text
    block='\n                ; Исходные байты обработчика близкой записи, память не выделяется\n                module ActionCloseRecordState\n'
    for label,address,note in (('InhibitCode',0xE507,'операнд LD A,n, 00 допускает корневой вход, ненулевой байт запрещает'),
        ('UnknownA794',0xA794,'состояние, обнуляемое общим хвостом для класса 12, игровой смысл не доказан')):
        block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionCloseRecordConst' not in text
    block='\n                ; Проверенные коды и пределы локальных входов E506 и E51F\n                module ActionCloseRecordConst\n'
    for label,value,note in (('IgnoredClass',0x14,'второй класс без обработки в корневом входе'),('TransferClass',0x12,'корневой класс передачи следующему режиму'),
        ('ComponentBit',4,'номер проверяемого бита ReuseByte дополнительного входа'),('HighLimit',4,'верхний исключённый предел преобразованного старшего байта')):
        block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for number,f in enumerate(new_functions):
        lines+=['                assert $ == #'+format(f['offset'],'04X'),'                disp #'+format(f['address'],'04X')]
        line='                include "../Action/'+f['name']+'.asm"'
        if number:line=line.ljust(80)+'; ('+str(number-1)+') жёсткий порядок дополнительного входа E51F'
        lines+=[line,'                ent']
    pending[path]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionCloseRecordFacts import FUNCTIONS as ACTION_CLOSE_RECORD_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_CLOSE_RECORD_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionCloseRecordFacts import CONTRACTS as ACTION_CLOSE_RECORD_CONTRACTS\nCONTRACTS.update(ACTION_CLOSE_RECORD_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_close_record_name_operands(region,function_address,operation)')
    text+="\nfrom ActionCloseRecordFacts import name_operands as action_close_record_name_operands\n"
    for address in facts.FUNCTIONS:text+=f"DOCUMENTS['Action',{address}]=('ActionCloseRecord','три входа обработки записи')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionCloseRecordFacts import COMMENTS as ACTION_CLOSE_RECORD_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_CLOSE_RECORD_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #'+format(following['address'],'04X')+' | [Action.'+following['name']+']';assert text.count(needle)==1
    rows=''.join('| #'+format(f['address'],'04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n' for f in new_functions)
    pending[path]=text.replace(needle,rows+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    sections=''.join('## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Различия трёх входов и модели](../ActionCloseRecord.md).\n\n' for f in new_functions)
    pending[path]=text.replace(needle,sections+needle).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');heading='## Код запрета близкой записи';assert heading not in text
    section='\n'+heading+'\n\nОперанд E507 принадлежит [DispatchCloseRecord](../Source/Action/DispatchCloseRecord.asm). Установлены писатели.\n\n'
    section+='\n'.join('- ['+format(pc,'04X')+'](../'+p+')→E507, один байт.' for pc,p in inhibit_writers)
    section+='\n\n[Уменьшение кода и различия входов](ActionCloseRecord.md) описаны отдельно.\n';pending[path]=(text+section).encode('utf-8')
    path=ROOT/'Docs/ActionObjectRecords.md';text=path.read_text('utf-8')
    text+='\n## Дополнительный потребитель ReuseByte\n\n[CheckCloseRecordComponents](ActionCloseRecord.md) проверяет только бит 4 ReuseByte, ноль направляет в общий хвост инверсии, единица допускает проверку старших байтов компонент. Другие потребители продолжают использовать полный байт, в том числе код FF. Это не переименование всего поля в набор независимых флагов.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionCloseRecord';history=ROOT/'Tools/Disasm/Research/History/BeforeActionCloseRecord'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и сверка всех текущих файлов перед публикацией.
    for current,before,after in plan:
        target=candidate/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current,before,after in plan:assert current.read_bytes()==before if before is not None else not current.exists()
    for current,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for current,before,after in plan:current.parent.mkdir(parents=True,exist_ok=True);current.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса после проверки и сохранения его истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x8506:0x855C]==(history/old['path']).read_bytes();old_path.unlink()
    result=dict(passed=True,described_functions=3,confirmed_code_bytes=86,confirmed_instructions=len(records),
        inhibit_writers_registered=len(inhibit_writers),model_cases=93184,original_bytes_preserved=True,
        auxiliary_entry_native_caller_proved=False,station_disk_load_executed=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionCloseRecordClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
