"""Выделение ACEA и его четырёх писателей операндов из исходного ресурса, без сборки."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionVectorWrapperFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionVectorWrapperVerification');assert proof['passed'] and proof['total_cases']==81152
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x4CAB)
    assert (old['length'],old['kind'])==(114,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x4CAB:0x4D1D]
    prefix='Source/Resources/17_ACTION/Unclassified022_BeforeVectorWrapper.bin'
    name,description=facts.FUNCTIONS[0xACEA];code_path='Source/Action/'+name+'.asm'
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    source_map[source_map.index(old):source_map.index(old)+1]=[
        piece(0x4CAB,0x4CEA,'unclassified',prefix,None),piece(0x4CEA,0x4D1D,'code',code_path,0xACEA)]
    instructions=decoder(flat_action()).disassemble(0xACEA,0xAD1D,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000) for i in instructions]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x4CEA:0x4D1D]
    region=next(r for r in flow if r['name']=='Action');assert not any(0xACEA<=i['address']<0xAD1D for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0xACEA,0xAD07});region['calls']=sorted(set(region['calls'])|{0xAD1D})
    region['branches']=sorted(set(region['branches'])|{0xAF43});region['instruction_count']+=len(records);region['code_bytes']+=51
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    for address,label in ((0xACEA,'Entry'),(0xAD07,'Resume')):
        key='Action.'+name+'.'+label;assert key not in symbols;symbols[key]=address
    index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>0xACEA)
    functions.insert(index,dict(region='Action',name=name,address=0xACEA,slot=17,offset=0x4CEA,
        description=description,semantic_status='described',end_offset=0x4D1D,path=code_path))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/('Tools/Disasm/Reports/'+stem+'.json'):encode(value) for stem,value in
        (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow))}
    modified=read('ModifiedCode')
    for writer,target,target_instruction,operation in ((0xACEE,0xAF48,0xAF47,'LD DE,#0000'),
        (0xACF1,0xAF56,0xAF55,'LD DE,#0000'),(0xACF5,0xAF69,0xAF68,'LD DE,#0000'),(0xACFC,0xAD08,0xAD07,'LD SP,#0000')):
        assert not any(i['region']=='Action' and i['writer']==writer for i in modified)
        modified.append(dict(region='Action',writer=writer,target=target,target_instruction=target_instruction,size=2,
            target_operation=operation,path=code_path))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']));pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
    pending[ROOT/prefix]=source[0x4CAB:0x4CEA]
    lines=['                module Action','                module '+name,
        '                ; Документация [транспонированная матрица и CPU-стек](../../Docs/ActionVectorWrapper.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, общая RAM банка 2, адреса ACEA..AD1C']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xACEA]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0xACEA,record['operation'].replace(',',', '));label='Entry' if pc==0xACEA else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionVectorWrapperState' not in text
    block='\n                ; Существующий операнд восстановления настоящего SP\n                module ActionVectorWrapperState\n'
    block+='SavedSP         equ #AD08'.ljust(80)+'; значение SP после PUSH IX и PUSH IY, память не выделяется\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    repl='                incbin "../Resources/17_ACTION/'+prefix.rsplit('/',1)[-1]+'"\n'
    repl+='                assert $ == #4CEA\n                disp #ACEA\n                include "../Action/'+name+'.asm"\n                ent'
    pending[path]=text.replace(needle,repl).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionVectorWrapperFacts import FUNCTIONS as ACTION_VECTOR_WRAPPER_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_VECTOR_WRAPPER_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionVectorWrapperFacts import CONTRACTS as ACTION_VECTOR_WRAPPER_CONTRACTS\nCONTRACTS.update(ACTION_VECTOR_WRAPPER_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_vector_wrapper_name_operands(region,function_address,operation)')
    text+="\nfrom ActionVectorWrapperFacts import name_operands as action_vector_wrapper_name_operands\nDOCUMENTS['Action',0xACEA]=('ActionVectorWrapper','транспонированная матрица и CPU-стек')\nLABELS['Action',0xAD07]='Resume'\n";pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionVectorWrapperFacts import COMMENTS as ACTION_VECTOR_WRAPPER_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_VECTOR_WRAPPER_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);needle='| #AD1D |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #ACEA | [Action.'+name+'](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## SwapCodePatchWords\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Контракт и композиционная модель](../ActionVectorWrapper.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');heading='## Сохранение компонентов и SP в ACEA';assert heading not in text
    text+='\n'+heading+'\n\n[TransformVectorTransposed](../Source/Action/TransformVectorTransposed.asm) записывает входные слова, ACEE→AF48, ACF1→AF56, ACF5→AF69, и настоящий SP, ACFC→AD08. Все записи двухбайтовые, относятся к существующим операндам. [Рамка и продолжение](ActionVectorWrapper.md) описаны отдельно.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionVectorWrapper';history=ROOT/'Tools/Disasm/Research/History/BeforeActionVectorWrapper';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка текущей рабочей копии до публикации.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление единственного заменённого ресурса после сохранения и сверки оригинала.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x4CAB:0x4D1D]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,confirmed_code_bytes=51,confirmed_instructions=len(records),
        compositional_model_cases=81152,independent_complete_child_oracle=False,physical_bytes_preserved=True,
        matrix_transpose_and_full_words_restored=True,maximum_additional_stack_bytes=6,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionVectorWrapperClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
