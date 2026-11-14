"""Защищённая публикация одного доказанного входа, целиком занимавшего исходный бинарный фрагмент."""
from collections import Counter
from pathlib import Path
import contextlib,hashlib,io,json,os,re,sys,tempfile
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
from CheckActionParameterActivation import flat_action
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main(facts,tag,start,end,expected_cases,allow_subrange=False,proof_tag=None):
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read((proof_tag or tag)+'Verification');assert proof['passed'] and proof['total_cases']==expected_cases
    assert list(facts.FUNCTIONS)==[start] and start<end
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();delta=0x23D if start<0x8000 else 0
    assert (end-1<0x8000)==(start<0x8000)
    offset,end_offset=start-0x6000+delta,end-0x6000+delta
    functions,source_map,symbols,inventory,flow,modified=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    previous_mutation_count=len(modified)
    old=next(i for i in source_map if i['slot']==17 and (i['offset']<=offset and end_offset<=i['offset']+i['length'] if allow_subrange else i['offset']==offset))
    assert old['kind']=='unclassified'
    if not allow_subrange:assert old['length']==end-start
    old_path=ROOT/old['path'];old_end=old['offset']+old['length']
    assert old_path.read_bytes()==source[old['offset']:old_end]
    instructions=decoder(flat_action()).disassemble(start,end,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000+delta) for i in instructions]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[offset:end_offset]
    name,description=facts.FUNCTIONS[start];code_path='Source/Action/'+name+'.asm';pending={}
    region=next(r for r in flow if r['name']=='Action');assert not any(start<=i['address']<end for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{start});calls=set(region['calls']);branches=set(region['branches'])
    for i in records:
        match=re.match(r'^(CALL|JP|JR|DJNZ) .*#([0-9A-F]{4})$',i['operation'])
        if match:(calls if match[1]=='CALL' else branches).add(int(match[2],16))
        if i['operation'] in ('JP (HL)','JP (IX)','JP (IY)'):
            assert not any(v['address']==i['address'] for v in region['unresolved'])
            region['unresolved'].append(dict(address=i['address'],operation=i['operation'],reason='косвенный переход'))
    region['calls'],region['branches']=sorted(calls),sorted(branches)
    region['instruction_count']+=len(records);region['code_bytes']+=end-start;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    validate_notes([region],{'Action':facts.COMMENTS})
    for address,label in ((start,'Entry'),*facts.LOCAL.items()):
        key='Action.'+name+'.'+label;assert key not in symbols;symbols[key]=address
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>start);following=functions[index]
    semantic_status=getattr(facts,'SEMANTIC_STATUS','described')
    assert semantic_status in ('described','unknown')
    if semantic_status=='unknown':assert proof.get('whole_procedure_proved') is False
    functions.insert(index,dict(region='Action',name=name,address=start,slot=17,offset=offset,end_offset=end_offset,path=code_path,description=description,semantic_status=semantic_status))
    pieces=[]
    if old['offset']<offset:
        prefix_path=getattr(facts,'UNCLASSIFIED_PREFIX_PATH',f'Source/Resources/17_ACTION/Unclassified{old["offset"]:04X}_{offset:04X}.bin')
        assert not (ROOT/prefix_path).exists(),('новый остаток не должен заменять существующий файл',prefix_path)
        pending[ROOT/prefix_path]=source[old['offset']:offset]
        pieces.append(dict(old,length=offset-old['offset'],path=prefix_path,origin=None,
            sha256=hashlib.sha256(source[old['offset']:offset]).hexdigest()))
    pieces.append(dict(old,offset=offset,length=end-start,kind='code',path=code_path,origin=start,
        sha256=hashlib.sha256(source[offset:end_offset]).hexdigest()))
    if end_offset<old_end:
        suffix_path=getattr(facts,'UNCLASSIFIED_SUFFIX_PATH',f'Source/Resources/17_ACTION/Unclassified{end_offset:04X}_{old_end:04X}.bin')
        assert not (ROOT/suffix_path).exists(),('новый остаток не должен заменять существующий файл',suffix_path)
        pending[ROOT/suffix_path]=source[end_offset:old_end]
        pieces.append(dict(old,offset=end_offset,length=old_end-end_offset,path=suffix_path,origin=None,
            sha256=hashlib.sha256(source[end_offset:old_end]).hexdigest()))
    source_map[source_map.index(old):source_map.index(old)+1]=pieces
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['unknown'] = inventory['fragments'] - inventory['described']
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    # Уточнение путей уже зарегистрированных писателей и целей при разделении их бинарного диапазона.
    for item in modified:
        if item.get('path')==old['path'] and item['region']=='Action':
            writer_offset=item.get('writer_offset',item['writer']-0x6000+delta)
            owner=next(p for p in pieces if p['offset']<=writer_offset<p['offset']+p['length'])
            item.update(path=owner['path'],writer_source_classified=owner['kind']=='code')
        target_bank = 5 if start < 0x8000 else 2 if start < 0xC000 else 0
        if item.get('target_path')==old['path']:
            assert item.get('target_slot')==17 and 'target_offset' in item
            owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
            item.update(target_path=owner['path'],target_source_classified=owner['kind']=='code')
        if item.get('target_region',item['region'])=='Action' and item.get('target_bank',target_bank)==target_bank and start<=item['target']<end:
            owner=next(i for i in records if i['address']<=item['target']<i['address']+len(bytes.fromhex(i['hex'])))
            assert item['target_instruction']==owner['address']
            item.update(target_source_classified=True,target_path=code_path)
    original=flat_action()
    for writer,target,instruction_address,size in getattr(facts,'MODIFIED_WRITERS',()):
        instruction=decoder(original).disassemble(instruction_address,instruction_address+1,'h')[0]
        assert instruction_address<target and target+size<=instruction_address+len(instruction.bytes)
        assert not any(i['region']=='Action' and i['writer']==writer for i in modified)
        modified.append(dict(region='Action',writer=writer,target=target,target_instruction=instruction_address,size=size,
            target_operation=instruction.operation,path=code_path))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']))
    if hasattr(facts,'qualify_mutations'):facts.qualify_mutations(modified,flow,functions,pieces)
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    lines=['                module Action','                module '+name,
        '                ; Документация [алгоритм и проверка](../../Docs/'+tag+'.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, адреса '+format(start,'04X')+'..'+format(end-1,'04X')]
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',start]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for i in records:
        pc=i['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=i['operation'].replace(',',', ')
        for address,label in facts.LOCAL.items():op=op.replace('#'+format(address,'04X'),'@Action.'+name+'.'+label)
        op=facts.name_operands('Action',start,op);label='Entry' if pc==start else facts.LOCAL.get(pc,'')
        assert len(label)<=15,('метка выходит за начало кода',label);line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule']
    continuation=following if getattr(facts,'FALLTHROUGH',False) else None
    if continuation:assert continuation['address']==end
    pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n',continuation).encode('utf-8')
    fields=getattr(facts,'STATE_FIELDS',())
    if fields:
        path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');module=getattr(facts,'STATE_MODULE',tag+'State');assert 'module '+module not in text
        block='\n                ; Существующие операнды и состояние, память не выделяется\n                module '+module+'\n'
        for label,address,note in fields:
            assert len(label)<=15;block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
        pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    # Удаление прежнего предупреждения только у заменяемого ресурса, новые неизвестные части получают свои комментарии.
    text=re.sub(r'(?m)^[ \t]*; Unknown, (?:соседние байты вне доказанного входа|исходные байты вне подтверждённого прямого потока управления)[^\n]*\n(?='+re.escape(needle)+r')','',text)
    include_lines=[]
    for piece in pieces:
        include_lines.append('                assert $ == #'+format(piece['offset'],'04X'))
        if piece['kind']=='code':
            include_lines+=['                disp #'+format(start,'04X'),'                include "../Action/'+name+'.asm"','                ent']
        else:
            include_lines+=['                ; Unknown, соседние байты вне доказанного входа '+name,
                            '                incbin "../Resources/17_ACTION/'+piece['path'].rsplit('/',1)[-1]+'"']
    pending[path]=text.replace(needle,'\n'.join(include_lines)).encode('utf-8')
    if hasattr(facts,'INCLUDE_ORDER'):
        owners=[next(f for f in functions if f['region']=='Action' and f['name']==value)
                for value in facts.INCLUDE_ORDER]
        assert all(a['slot']==b['slot'] and a['end_offset']==b['offset'] for a,b in zip(owners,owners[1:]))
        ordered=pending[path].decode('utf-8')
        for number,value in enumerate(facts.INCLUDE_ORDER):
            line='                include "../Action/'+value+'.asm"'
            pattern=r'(?m)^'+re.escape(line)+r'(?:[ \t]+; \(\d+\) жёсткий порядок, последовательное исполнение)?$'
            ordered,count=re.subn(pattern,line.ljust(80)+'; ('+str(number)+') жёсткий порядок, последовательное исполнение',ordered)
            assert count==1
        pending[path]=ordered.encode('utf-8')
    prefix=re.sub(r'(?<!^)(?=[A-Z][a-z])','_',tag).upper();handler=prefix.lower()+'_name_operands'
    for filename,extra in (
        ('Knowledge.py',f"\nfrom {tag}Facts import FUNCTIONS as {prefix}_FUNCTIONS\nFUNCTIONS['Action'].update({prefix}_FUNCTIONS)\n"),
        ('Contracts.py',f"\nfrom {tag}Facts import CONTRACTS as {prefix}_CONTRACTS\nCONTRACTS.update({prefix}_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = '+handler+'(region,function_address,operation)')
    text+=f"\nfrom {tag}Facts import name_operands as {handler}\nDOCUMENTS['Action',{start}]=('{tag}','алгоритм и проверка')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,f"\nfrom {tag}Facts import COMMENTS as {prefix}_COMMENTS\nREGION_COMMENTS.setdefault('Action',{{}}).update({prefix}_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #'+format(following['address'],'04X')+' | [Action.'+following['name']+']';assert text.count(needle)==1
    row='| #'+format(start,'04X')+' | [Action.'+name+'](../'+code_path+') | '+description+' |\n';pending[path]=text.replace(needle,row+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Алгоритм, точные регистры и модель](../'+tag+'.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    writers=getattr(facts,'MODIFIED_WRITERS',())
    if writers:
        path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');heading='## '+name
        assert heading not in text
        section='\n'+heading+'\n\n['+name+'](../'+code_path+') обновляет следующие существующие операнды в контексте своего договора.\n\n'
        section+='\n'.join('- '+format(writer,'04X')+'→'+format(target,'04X')+', '+str(size)+' байт, инструкция по '+format(instruction,'04X')+'.' for writer,target,instruction,size in writers)
        section+='\n\n[Алгоритм и ограничения](./'+tag+'.md) описаны отдельно.\n';pending[path]=(text+section).encode('utf-8')
    for relative,marker,block in getattr(facts,'INCLUDE_BLOCKS',()):
        path=ROOT/relative
        assert path.resolve().is_relative_to(ROOT.resolve())
        text=pending.get(path,path.read_bytes()).decode('utf-8')
        assert marker not in text and text.count('                endif')==1
        pending[path]=text.replace('                endif',block+'\n                endif').encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag);history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Подготовка отдельного кандидата и сверка всех текущих файлов до публикации.
    for current,before,after in plan:
        target=candidate/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current,before,after in plan:assert current.read_bytes()==before if before is not None else not current.exists()
    for current,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for current,before,after in plan:
        current.parent.mkdir(parents=True,exist_ok=True)
        if current.suffix != '.json' and len(after) < 4_000_000:
            current.write_bytes(after)
            continue
        # Большой реестр заменяется целиком после записи временной копии в той же папке.
        with tempfile.NamedTemporaryFile(dir=current.parent, prefix='candidate-', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            output.write(after)
        try:
            os.replace(temporary, current)
        finally:
            if temporary.exists():
                temporary.unlink()
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённого ресурса, его байты сохранены в оригинале и истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[old['offset']:old_end]==(history/old['path']).read_bytes();old_path.unlink()
    result=dict(passed=True,described_functions=int(semantic_status=='described'),semantic_status=semantic_status,confirmed_code_bytes=end-start,confirmed_instructions=len(records),
        model_cases=expected_cases,original_bytes_preserved=True,self_modifying_writers_registered=len(modified)-previous_mutation_count,assembly_executed=False)
    (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_bytes(encode(result));print(json.dumps(result,indent=2))
