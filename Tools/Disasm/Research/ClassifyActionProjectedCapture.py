"""Выделение локального выбора и двух явно неизвестных соседних фрагментов из исходного продолжения E020."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from CheckActionParameterActivation import flat_action
import ActionProjectedCaptureFacts as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionProjectedCaptureVerification');assert proof['passed'] and proof['total_cases']==262550
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x81B9)
    assert (old['length'],old['kind'])==(749,'unclassified');old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x81B9:0x84A6]
    instructions=decoder(flat_action()).disassemble(0xE1B9,0xE4A6,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000) for i in instructions]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x81B9:0x84A6]
    starts={i['address'] for i in records};assert {0xE1B9,0xE30F,0xE36A}<=starts
    blocks=((0xE1B9,0xE30F,'UnknownE1B9'),(0xE30F,0xE36A,'CaptureProjectedRecord'),(0xE36A,0xE4A6,'UnknownE36A'))
    region=next(r for r in flow if r['name']=='Action');assert not any(0xE1B9<=i['address']<0xE4A6 for i in region['instructions'])
    # Проверка границ всех статических целей, самомодифицируемые JR остаются явно отмеченными неизвестными частями.
    targets={};calls=set();branches=set()
    for record in records:
        match=re.match(r'^(CALL|JP|JR|DJNZ) .*#([0-9A-F]{4})$',record['operation'])
        if match:
            target=int(match[2],16);targets[record['address']]=target
            (calls if match[1]=='CALL' else branches).add(target)
            assert target in starts if 0xE1B9<=target<0xE4A6 else True
    new_functions=[];new_ranges=[];pending={};named={}
    for start,end,name in blocks:
        path='Source/Action/'+name+'.asm';described=start==0xE30F
        description=facts.FUNCTIONS[start][1] if described else 'Unknown, окружающий обход проекции и его полный договор ещё не доказаны'
        new_functions.append(dict(region='Action',name=name,address=start,slot=17,offset=start-0x6000,
            description=description,semantic_status='described' if described else 'unknown',end_offset=end-0x6000,path=path))
        new_ranges.append(dict(slot=17,offset=start-0x6000,length=end-start,kind='code',path=path,origin=start,
            sha256=hashlib.sha256(source[start-0x6000:end-0x6000]).hexdigest()))
        for pc in sorted(({start}|set(targets.values())|set(facts.LOCAL))&starts):
            if not start<=pc<end:continue
            label='Entry' if pc==start else facts.LOCAL.get(pc,'Point'+format(pc,'04X'))
            key='Action.'+name+'.'+label;assert key not in symbols;symbols[key]=pc;named[pc]=key
    for key,value in symbols.items():
        if key.startswith('Action.') and value not in named:named[value]=key
    for number,function in enumerate(new_functions):
        start,end=function['address'],function['end_offset']+0x6000;name=function['name'];described=start==0xE30F
        lines=['                module Action','                module '+name,
            '                ; Документация [локальный выбор и неизвестный обход](../../Docs/ActionProjectedCapture.md)',
            '                ; -----------------------------------------','                ; '+function['description'],
            '                ; исходная запись 17, код ACTION банка 0, адреса '+format(start,'04X')+'..'+format(end-1,'04X')]
        contracts=facts.CONTRACTS['Action',start] if described else (
            ['Unknown, полный регистровый договор окружающего обхода ещё не доказан'],
            ['Unknown, исходные переходы сохранены, назначение всех полей и выходов ещё не установлено'],
            ["Unknown, включая HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP и изменяемый код"],
            ['это выделение исходных инструкций, оно не доказывает полный алгоритм окружающего обхода',
             'самомодифицируемые JR, переиспользование SP и внешние вызовы требуют дальнейшего разбора'])
        for heading,values in zip(('In','Out','Corrupt','Note'),contracts):lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
        lines.append('                ; -----------------------------------------')
        for record in records:
            pc=record['address']
            if not start<=pc<end:continue
            before,right=facts.COMMENTS.get(pc,([],None)) if described else ([],None)
            lines+=['                ; '+v for v in before];op=record['operation'].replace(',',', ')
            if pc in targets and targets[pc] in named:op=op.replace('#'+format(targets[pc],'04X'),'@'+named[targets[pc]])
            op=facts.name_operands('Action',start,op)
            label=named[pc].rsplit('.',1)[1] if pc in named and named[pc].startswith('Action.'+name+'.') else ''
            line=((label+':').ljust(16) if label else ' '*16)+op
            if not right:
                match=re.match(r'^(JR|JP|CALL|RET) (NZ|Z|NC|C|PO|PE|P|M)(?:,|$)',record['operation'])
                if match:
                    condition={'NZ':'Z сброшен','Z':'Z установлен','NC':'Carry сброшен','C':'Carry установлен',
                        'PO':'P/V сброшен','PE':'P/V установлен','P':'Sign сброшен','M':'Sign установлен'}[match[2]]
                    right=('выход' if match[1]=='RET' else 'вызов' if match[1]=='CALL' else 'переход')+', если флаг '+condition
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        lines+=['                endmodule','                endmodule']
        target=new_functions[number+1] if number<2 else None
        pending[ROOT/function['path']]=format_function('\n'.join(lines)+'\n',target).encode('utf-8')
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{f['address'] for f in new_functions});region['calls']=sorted(set(region['calls'])|calls)
    region['branches']=sorted(set(region['branches'])|branches);region['instruction_count']+=len(records);region['code_bytes']+=749
    region['classified_fraction']=region['code_bytes']/region['total_bytes'];validate_notes([region],{'Action':facts.COMMENTS})
    index=source_map.index(old);source_map[index:index+1]=new_ranges
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>0xE1B9)
    following=functions[index];functions[index:index]=new_functions
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    modified=read('ModifiedCode');all_instructions=region['instructions']
    for record in records:
        match=re.fullmatch(r'LD \(#([0-9A-F]{4})\),(A|HL|DE|BC|SP)',record['operation'])
        if not match:continue
        target=int(match[1],16);size=1 if match[2]=='A' else 2
        instruction=next((i for i in all_instructions if i['address']<target<i['address']+len(bytes.fromhex(i['hex']))),None)
        if instruction is None:continue
        assert not any(i['region']=='Action' and i['writer']==record['address'] for i in modified)
        path=next(f['path'] for f in new_functions if f['address']<=record['address']<f['end_offset']+0x6000)
        modified.append(dict(region='Action',writer=record['address'],target=target,target_instruction=instruction['address'],
            size=size,target_operation=instruction['operation'],path=path))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for number,f in enumerate(new_functions,1):
        lines+=['                disp #'+format(f['address'],'04X'),('                include "../Action/'+f['name']+'.asm"').ljust(80)+'; ('+str(number)+') жёсткий порядок продолжения E020','                ent']
    text=text.replace(needle,'\n'.join(lines));needle='                include "../Action/UnknownE020.asm"';assert text.count(needle)==1
    text=text.replace(needle,needle.ljust(80)+'; (0) жёсткий порядок продолжения E020');pending[path]=text.encode('utf-8')
    path=ROOT/'Source/Action/UnknownE020.asm';text=path.read_text('utf-8')
    pending[path]=format_function(text,new_functions[0]).encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionProjectedCaptureState' not in text
    block='\n                ; Существующие операнды локальной проверки двух допусков\n                module ActionProjectedCaptureState\n'
    for name,address,note in (('Gate',0xE310,'ненулевой байт запрещает запись результата'),('Limit',0xE331,'беззнаковое слово допуска обеих осей'),('ProjectedX',0xE33A,'слово второй координаты до signed8-поправки')):
        block+=(name.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionProjectedCaptureFacts import FUNCTIONS as ACTION_PROJECTED_CAPTURE_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_PROJECTED_CAPTURE_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionProjectedCaptureFacts import CONTRACTS as ACTION_PROJECTED_CAPTURE_CONTRACTS\nCONTRACTS.update(ACTION_PROJECTED_CAPTURE_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_projected_capture_name_operands(region,function_address,operation)')
    text+="\nfrom ActionProjectedCaptureFacts import name_operands as action_projected_capture_name_operands\nDOCUMENTS['Action',0xE30F]=('ActionProjectedCapture','локальная проверка допуска')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionProjectedCaptureFacts import COMMENTS as ACTION_PROJECTED_CAPTURE_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTED_CAPTURE_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);needle='| #'+format(following['address'],'04X')+' |';assert text.count(needle)==1
    rows=''.join('| #'+format(f['address'],'04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n' for f in new_functions)
    pending[path]=text.replace(needle,rows+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    sections=''.join('## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Границы локального доказательства](../ActionProjectedCapture.md).\n\n' for f in new_functions)
    pending[path]=text.replace(needle,sections+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionProjectedCapture';history=ROOT/'Tools/Disasm/Research/History/BeforeActionProjectedCapture'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Подготовка отдельного кандидата и защита текущих ручных правок перед публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только заменённого исходного ресурса после проверки и сохранения его истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==(history/old_path.relative_to(ROOT)).read_bytes()==source[0x81B9:0x84A6];old_path.unlink()
    result=dict(passed=True,described_functions=1,new_explicit_unknown_fragments=2,confirmed_code_bytes=749,
        confirmed_instructions=len(records),proved_local_code_bytes=91,model_cases=262550,whole_projection_scan_proved=False,
        physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectedCaptureClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
