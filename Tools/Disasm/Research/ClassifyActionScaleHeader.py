"""Отделение 24 доказанных байтов от неизвестного продолжения с сохранением ручных исходников."""
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionScaleHeaderFacts as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionScaleHeaderVerification');assert proof['passed'] and proof['total_cases']==1920
    functions,source_map,symbols,inventory,flow,modified=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    old=next(f for f in functions if f['region']=='Action' and f['address']==0xE1B9)
    assert (old['name'],old['offset'],old['end_offset'])==('UnknownE1B9',0x81B9,0x830F)
    old_path=ROOT/old['path'];old_text=old_path.read_text('utf-8');old_range=next(i for i in source_map if i['path']==old['path'])
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();pending={}
    name,description=facts.FUNCTIONS[0xE1B9];path='Source/Action/'+name+'.asm'
    first=dict(old,name=name,description=description,path=path,semantic_status='described',end_offset=0x81D1)
    second=dict(old,name='UnknownE1D1',address=0xE1D1,offset=0x81D1,path='Source/Action/UnknownE1D1.asm')
    rename_symbols={}
    for key,value in symbols.items():
        if not key.startswith('Action.UnknownE1B9.'):continue
        if value==0xE1B9:new='Action.'+name+'.Entry'
        elif value==0xE1C7:new='Action.'+name+'.SelectShifts'
        else:new=key.replace('Action.UnknownE1B9.','Action.UnknownE1D1.')
        rename_symbols[key]=new
    def rename(text):
        for before,after in rename_symbols.items():text=re.sub(r'\b'+re.escape(before)+r'\b',after,text)
        return text.replace('/Action/UnknownE1B9.asm','/Action/'+name+'.asm').replace('продолжение в UnknownE1B9.asm','продолжение в '+name+'.asm')
    # Поиск только существующих ссылок на переносимые метки, окружающий пользовательский код не переоформляется.
    for directory,patterns in (('Source',('*.asm','*.inc')),('Docs',('*.md',))):
        for pattern in patterns:
            for current in (ROOT/directory).rglob(pattern):
                if current==old_path:continue
                text=current.read_text('utf-8');after=rename(text)
                if after!=text:pending[current]=after.encode('utf-8')
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if 0xE1B9<=i['address']<0xE1D1]
    assert len(records)==13 and b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x81B9:0x81D1]
    validate_notes([region],{'Action':facts.COMMENTS})
    lines=['                module Action','                module '+name,
        '                ; Документация [масштаб заголовка](../../Docs/ActionScaleHeader.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, код ACTION банка 0, адреса E1B9..E1D0']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xE1B9]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=record['operation'].replace(',',', ').replace('JR #E1C7','JR @Action.'+name+'.SelectShifts')
        op=facts.name_operands('Action',0xE1B9,op);label='Entry' if pc==0xE1B9 else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',second).encode('utf-8')
    # Сохранение неизвестного хвоста текстом исходной рабочей копии, изменяются только модуль и перенесённые ссылки.
    begin=old_text.index('Entry:');cut=old_text.index('                PUSH BC\n',begin)
    header=old_text[:begin].replace('module UnknownE1B9','module UnknownE1D1').replace('E1B9..E30E','E1D1..E30E')
    tail=rename(old_text[cut:]);tail=tail.replace('                PUSH BC\n','Entry:          PUSH BC\n',1)
    pending[ROOT/second['path']]=(header+tail).encode('utf-8')
    index=functions.index(old);functions[index:index+1]=[first,second]
    index=source_map.index(old_range)
    ranges=[]
    for f in (first,second):
        start,end=f['offset'],f['end_offset'];ranges.append(dict(old_range,offset=start,length=end-start,path=f['path'],origin=f['address'],sha256=hashlib.sha256(source[start:end]).hexdigest()))
    source_map[index:index+1]=ranges
    symbols={rename_symbols.get(k,k):v for k,v in symbols.items()};assert 'Action.UnknownE1D1.Entry' not in symbols
    symbols['Action.UnknownE1D1.Entry']=0xE1D1;region['roots']=sorted(set(region['roots'])|{0xE1D1})
    for item in modified:
        if item['path']==old['path']:item['path']=first['path'] if item['writer']<0xE1D1 else second['path']
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']!='described' for f in functions))
    inventory['ranges_by_kind']['code']+=1
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    current=ROOT/'Source/Files/17_ACTION.inc';text=pending[current].decode('utf-8')
    line=next(l for l in text.splitlines() if 'include "../Action/'+name+'.asm"' in l)
    repl=('                include "../Action/'+name+'.asm"').ljust(80)+'; (1) жёсткий порядок продолжения E020\n'
    repl+='                ent\n                assert $ == #81D1\n                disp #E1D1\n'
    repl+='                include "../Action/UnknownE1D1.asm"'.ljust(80)+'; (2) жёсткий порядок продолжения E020'
    text=text.replace(line,repl)
    for filename,before,after in (('CaptureProjectedRecord.asm','(2)','(3)'),('UnknownE36A.asm','(3)','(4)')):
        line=next(l for l in text.splitlines() if 'include "../Action/'+filename+'"' in l)
        assert before in line;text=text.replace(line,line.replace(before,after))
    pending[current]=text.encode('utf-8')
    current=ROOT/'Includes/Variables/Include.inc';text=current.read_text('utf-8');assert 'module ActionScaleHeaderState' not in text
    block='\n                ; Существующие операнды масштаба заголовка, память не выделяется\n                module ActionScaleHeaderState\n'
    for label,address,note in (('SizeSkip',0xE1C8,'смещение первого JR, число пропущенных удвоений'),
        ('FirstAxisSkip',0xE232,'смещение следующего JR первой оси'),('SecondAxisSkip',0xE26B,'смещение следующего JR второй оси'),
        ('ScaledBound',0xE2C5,'операнд LD HL,nn, результат масштабирования мантиссы')):
        block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
    pending[current]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionScaleHeaderFacts import FUNCTIONS as ACTION_SCALE_HEADER_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_SCALE_HEADER_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionScaleHeaderFacts import CONTRACTS as ACTION_SCALE_HEADER_CONTRACTS\nCONTRACTS.update(ACTION_SCALE_HEADER_CONTRACTS)\n")):
        current=ROOT/'Tools/Disasm/Research'/filename;text=current.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[current]=(text+extra).encode('utf-8')
    current=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=current.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_scale_header_name_operands(region,function_address,operation)')
    text+="\nfrom ActionScaleHeaderFacts import name_operands as action_scale_header_name_operands\nDOCUMENTS['Action',0xE1B9]=('ActionScaleHeader','масштабирование заголовка')\nLABELS['Action',0xE1C7]='SelectShifts'\n"
    pending[current]=text.encode('utf-8')
    current=ROOT/'Tools/Disasm/Research/ExportSources.py';text=current.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[current]=text.replace(needle,"\nfrom ActionScaleHeaderFacts import COMMENTS as ACTION_SCALE_HEADER_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_SCALE_HEADER_COMMENTS)\n"+needle).encode('utf-8')
    current=ROOT/'Docs/Functions.md';text=pending[current].decode('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    old_line=next(l for l in text.splitlines() if l.startswith('| #E1B9 |'))
    rows='\n'.join('| #'+format(f['address'],'04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |' for f in (first,second))
    pending[current]=text.replace(old_line,rows).encode('utf-8')
    current=ROOT/'Docs/FunctionDetails/Action.md';text=pending[current].decode('utf-8');start=text.index('## UnknownE1B9\n');end=text.find('\n## ',start+4)
    assert end>start
    sections=''.join('## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Масштаб и границы проверки](../ActionScaleHeader.md).\n\n' for f in (first,second))
    pending[current]=(text[:start]+sections+text[end:]).encode('utf-8')
    current=ROOT/'Docs/ActionProjectedCapture.md';text=pending[current].decode('utf-8')
    text=text.replace('[UnknownE1B9](../Source/Action/'+name+'.asm)','[UnknownE1D1](../Source/Action/UnknownE1D1.asm)')
    text=text.replace('четыре части (0)..(3)','пять частей (0)..(4)')
    text+='\nНачальные 24 байта подготовки выделены в [PrepareProjectionScale](ActionScaleHeader.md), следующие 318 байтов до E30F остаются UnknownE1D1. Установленный масштаб не доказывает весь окружающий обход.\n';pending[current]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionScaleHeader';history=ROOT/'Tools/Disasm/Research/History/BeforeActionScaleHeader'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка отсутствия новых ручных изменений, индекс Git не затрагивается.
    for current,before,after in plan:
        target=candidate/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current,before,after in plan:assert current.read_bytes()==before if before is not None else not current.exists()
    for current,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for current,before,after in plan:current.parent.mkdir(parents=True,exist_ok=True);current.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только переименованного исходника после проверки и сохранения его точной истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Action').resolve()) and old_path.read_bytes()==(history/old['path']).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,proved_local_code_bytes=24,confirmed_instructions=13,
        remaining_unknown_code_bytes=318,original_bytes_preserved=True,model_cases=1920,whole_projection_scan_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionScaleHeaderClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
