"""Четыре адресных преобразователя, сохранение двух Unknown-контрольных копий, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionRecordIndexFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionRecordIndexVerification');assert proof['passed'] and proof['total_cases']==262144
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old_functions=[f for f in functions if f['region']=='Action' and f['address'] in (0xE6BE,0xE6C7)]
    assert len(old_functions)==2 and all(f['semantic_status']=='unknown' for f in old_functions)
    old_names={f['name']:facts.FUNCTIONS[f['address']][0] for f in old_functions}
    removed={ROOT/f['path']:(ROOT/f['path']).read_bytes() for f in old_functions}
    raw=[next(i for i in source_map if i['slot']==17 and i['offset']==offset) for offset in (0x869E,0x86C5)]
    for item in raw:
        path=ROOT/item['path'];assert path.read_bytes()==source[item['offset']:item['offset']+item['length']];removed[path]=path.read_bytes()
    assert [i['length'] for i in raw]==[32,2]
    pending={}
    def rename(text):
        for before,after in old_names.items():text=text.replace(before,after)
        return text
    # Поиск только ссылок на два переименовываемых входа, без форматирования постороннего кода.
    for folder,pattern in (('Source','*.asm'),('Source','*.inc'),('Docs','*.md')):
        for path in (ROOT/folder).rglob(pattern):
            if path in removed:continue
            before=path.read_text('utf-8');after=rename(before)
            if after!=before:
                lines=after.splitlines()
                for i,line in enumerate(lines):
                    code,sep,note=line.partition(';')
                    if sep and code.strip():
                        assert len(code.rstrip())<80;lines[i]=code.rstrip().ljust(80)+';'+note
                pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    start=source_map.index(raw[0]);finish=source_map.index(next(i for i in source_map if i['path']=='Source/Action/UnknownE6C7.asm'))+1
    prefix='Source/Resources/17_ACTION/Unclassified035_BeforeRecordIndex.bin';pending[ROOT/prefix]=source[0x869E:0x86A7]
    bounds=((0xE6A7,0xE6B5),(0xE6B5,0xE6BE),(0xE6BE,0xE6C7),(0xE6C7,0xE6D1))
    source_map[start:finish]=[piece(0x869E,0x86A7,'unclassified',prefix,None)]+[
        piece(a-0x6000,b-0x6000,'code','Source/Action/'+facts.FUNCTIONS[a][0]+'.asm',a) for a,b in bounds]
    first=functions.index(old_functions[0]);functions[first:first+2]=[
        dict(region='Action',name=facts.FUNCTIONS[a][0],address=a,slot=17,offset=a-0x6000,
            description=facts.FUNCTIONS[a][1],semantic_status='described',end_offset=b-0x6000,
            path='Source/Action/'+facts.FUNCTIONS[a][0]+'.asm') for a,b in bounds]
    symbols={rename(k):v for k,v in symbols.items()}
    for a,(name,description) in facts.FUNCTIONS.items():symbols['Action.'+name+'.Entry']=a
    region=next(r for r in flow if r['name']=='Action')
    instructions=decoder(flat_action()).disassemble(0xE6A7,0xE6D1,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000) for i in instructions]
    assert len(records)==27 and b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x86A7:0x86D1]
    existing={i['address']:i for i in region['instructions'] if 0xE6A7<=i['address']<0xE6D1}
    assert len(existing)==11 and all(existing[i['address']]==i for i in records if i['address'] in existing)
    region['instructions']=sorted([i for i in region['instructions'] if not 0xE6A7<=i['address']<0xE6D1]+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS));region['calls']=sorted(set(region['calls'])|{0xE6C7})
    region['instruction_count']+=16;region['code_bytes']+=25;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    for a,b in bounds:
        name,description=facts.FUNCTIONS[a]
        lines=['                module Action','                module '+name,
            '                ; Документация [коды и адреса записей](../../Docs/ActionRecordIndex.md)',
            '                ; -----------------------------------------','                ; '+description,
            '                ; исходная запись 17, код ACTION банка 0, адреса '+format(a,'04X')+'..'+format(b-1,'04X')]
        for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',a]):
            lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
        lines+=['                ; -----------------------------------------']
        for record in records:
            pc=record['address']
            if not a<=pc<b:continue
            before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
            op=facts.name_operands('Action',a,record['operation'].replace(',',', '))
            line=('Entry:          ' if pc==a else ' '*16)+op
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        lines+=['                endmodule','                endmodule']
        pending[ROOT/('Source/Action/'+name+'.asm')]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
        unknown=sum(f['semantic_status']!='described' for f in functions),instructions=inventory['instructions']+16)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    modified=read('ModifiedCode')
    for item in modified:item['path']=rename(item['path'])
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionRecordIndexConst' not in text
    block='\n                ; Старший байт исходной базы записей A100, память не выделяется\n                module ActionRecordIndexConst\n'
    block+='BaseHigh        equ #A1'.ljust(80)+'; база преобразований с шагом 64 байта\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=pending.get(path,path.read_bytes()).decode('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+PathName(raw[0]['path'])+'"';assert text.count(needle)==1
    repl='                incbin "../Resources/17_ACTION/'+prefix.rsplit('/',1)[-1]+'"\n'
    for a,b in bounds[:2]:
        repl+='                assert $ == #'+format(a-0x6000,'04X')+'\n                disp #'+format(a,'04X')+'\n                include "../Action/'+facts.FUNCTIONS[a][0]+'.asm"\n                ent\n'
    text=text.replace(needle,repl.rstrip())
    needle='                incbin "../Resources/17_ACTION/'+PathName(raw[1]['path'])+'"';assert text.count(needle)==1
    # Удаление только исходного утверждения промежуточной границы, обёртка теперь включает POP HL и RET.
    old_assert='                assert $ == #86C5';assert text.count(old_assert)==1
    text=text.replace(old_assert+'\n                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'+needle+'\n','')
    pending[path]=text.encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionRecordIndexFacts import FUNCTIONS as ACTION_RECORD_INDEX_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_RECORD_INDEX_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionRecordIndexFacts import CONTRACTS as ACTION_RECORD_INDEX_CONTRACTS\nCONTRACTS.update(ACTION_RECORD_INDEX_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_record_index_name_operands(region,function_address,operation)')
    text+="\nfrom ActionRecordIndexFacts import name_operands as action_record_index_name_operands\nDOCUMENTS.update({('Action',a):('ActionRecordIndex','коды и адреса записей') for a in (0xE6A7,0xE6B5,0xE6BE,0xE6C7)})\n";pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionRecordIndexFacts import COMMENTS as ACTION_RECORD_INDEX_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_RECORD_INDEX_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #E6BE |';assert text.count(needle)==1
    newrows=''.join('| #'+format(a,'04X')+' | [Action.'+facts.FUNCTIONS[a][0]+'](../Source/Action/'+facts.FUNCTIONS[a][0]+'.asm) | '+facts.FUNCTIONS[a][1]+' |\n' for a,b in bounds[:2])
    text=text.replace(needle,newrows+needle)
    for a,b in bounds[2:]:
        start=text.index('| #'+format(a,'04X')+' |');end=text.index('\n',start)
        text=text[:start]+text[start:end].replace('Unknown, назначение этого фрагмента ещё не установлено',facts.FUNCTIONS[a][1])+text[end:]
    pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    def section(a):
        n,d=facts.FUNCTIONS[a];return '## '+n+'\n\n[Action.'+n+'](../../Source/Action/'+n+'.asm)\n\n'+d+'.\n\n[Контракт и независимая модель](../ActionRecordIndex.md).\n\n'
    for a,b in bounds[2:]:
        start=text.index('## '+facts.FUNCTIONS[a][0]+'\n');end=text.find('\n## ',start+4);end=len(text) if end<0 else end
        text=text[:start]+section(a)+text[end:]
    needle='## RecordIYToIndex\n';text=text.replace(needle,''.join(section(a) for a,b in bounds[:2])+needle);pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRecordIndex';history=ROOT/'Tools/Disasm/Research/History/BeforeActionRecordIndex';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка текущей рабочей копии до замены.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},**removed}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только четырёх заменённых файлов после сохранения и проверки исходных копий.
    for path,before in removed.items():
        assert path.resolve().is_relative_to((ROOT/'Source').resolve())
        assert path.read_bytes()==before==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
    report=dict(passed=True,described_functions=4,removed_unknown_fragments=2,newly_confirmed_code_bytes=25,
        newly_confirmed_instructions=16,independent_model_cases=262144,physical_bytes_preserved=True,
        record_field_meanings_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordIndexClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


def PathName(path):return path.rsplit('/',1)[-1]


if __name__=='__main__':main()
