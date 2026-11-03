"""Выделение 43 исходных байтов обмена слов, без сборки и переноса адресов."""
from collections import Counter
import contextlib,hashlib,io,json,re,sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
import ActionPatchSwapFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionPatchSwapVerification');assert proof['passed'] and proof['total_cases']==196864
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    old=next(i for i in source_map if i['slot']==17 and i['offset']==0x4CAB)
    assert (old['length'],old['kind'])==(157,'unclassified')
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x4CAB:0x4D48]
    prefix='Source/Resources/17_ACTION/Unclassified022_BeforePatchSwap.bin'
    name,description=facts.FUNCTIONS[0xAD1D];code_path='Source/Action/'+name+'.asm'
    def piece(start,end,kind,path,origin):return dict(slot=17,offset=start,length=end-start,kind=kind,path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    source_map[source_map.index(old):source_map.index(old)+1]=[
        piece(0x4CAB,0x4D1D,'unclassified',prefix,None),piece(0x4D1D,0x4D48,'code',code_path,0xAD1D)]
    instructions=decoder(flat_action()).disassemble(0xAD1D,0xAD48,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=17,offset=i.address-0x6000) for i in instructions]
    assert len(records)==13 and b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x4D1D:0x4D48]
    region=next(r for r in flow if r['name']=='Action');assert not any(0xAD1D<=i['address']<0xAD48 for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|{0xAD1D});region['instruction_count']+=13;region['code_bytes']+=43
    region['classified_fraction']=region['code_bytes']/region['total_bytes']
    key='Action.'+name+'.Entry';assert key not in symbols;symbols[key]=0xAD1D
    function_index=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>0xAD1D)
    functions.insert(function_index,dict(region='Action',name=name,address=0xAD1D,slot=17,offset=0x4D1D,
        description=description,semantic_status='described',end_offset=0x4D48,path=code_path))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+13)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    pending={ROOT/('Tools/Disasm/Reports/'+stem+'.json'):encode(value) for stem,value in
        (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow))}
    modified=read('ModifiedCode')
    for writer,target in ((0xAD24,0xCB54),(0xAD27,0xCB8B),(0xAD32,0xCB6F),(0xAD35,0xCBD8),(0xAD40,0xCBBC),(0xAD43,0xCBEE)):
        assert not any(i['region']=='Action' and i['writer']==writer for i in modified)
        modified.append(dict(region='Action',writer=writer,target=target,target_instruction=target-1,size=2,
            target_operation='LD A,#00',path=code_path))
    modified.sort(key=lambda i:(i['region'],i['writer'],i['target']))
    pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
    pending[ROOT/prefix]=source[0x4CAB:0x4D1D]
    lines=['                module Action','                module '+name,
        '                ; Документация [обмен слов кода](../../Docs/ActionPatchSwap.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, общая RAM банка 2, адреса AD1D..AD47']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xAD1D]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0xAD1D,record['operation'].replace(',',', '))
        line=('Entry:          ' if pc==0xAD1D else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionPatchSwapState' not in text
    block='\n                ; Существующие слова изменяемого кода банка 0, память не выделяется\n                module ActionPatchSwapState\n'
    for index,pair in enumerate(facts.PAIRS):
        for side,address in zip(('A','B'),pair):
            block+=('Pair'+str(index)+side).ljust(16)+('equ #'+format(address,'04X')).ljust(64)+'; операнд LD A,n и следующий байт кода, полное слово обмена\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    repl='                incbin "../Resources/17_ACTION/'+prefix.rsplit('/',1)[-1]+'"\n'
    repl+='                assert $ == #4D1D\n                disp #AD1D\n                include "../Action/'+name+'.asm"\n                ent'
    pending[path]=text.replace(needle,repl).encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionPatchSwapFacts import FUNCTIONS as ACTION_PATCH_SWAP_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_PATCH_SWAP_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionPatchSwapFacts import CONTRACTS as ACTION_PATCH_SWAP_CONTRACTS\nCONTRACTS.update(ACTION_PATCH_SWAP_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_patch_swap_name_operands(region,function_address,operation)')
    text+="\nfrom ActionPatchSwapFacts import name_operands as action_patch_swap_name_operands\nDOCUMENTS['Action',0xAD1D]=('ActionPatchSwap','обмен слов кода')\n";pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionPatchSwapFacts import COMMENTS as ACTION_PATCH_SWAP_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_PATCH_SWAP_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    # Поиск следующего известного входа для сохранения адресного порядка реестра.
    following=functions[function_index+1];needle='| #'+format(following['address'],'04X')+' |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #AD1D | [Action.'+name+'](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## '+following['name']+'\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Контракт и независимая модель](../ActionPatchSwap.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPatchSwap';history=ROOT/'Tools/Disasm/Research/History/BeforeActionPatchSwap';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка текущих пользовательских файлов до замены.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление единственного заменённого ресурса после сохранения и проверки оригинала.
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x4CAB:0x4D48]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    report=dict(passed=True,described_functions=1,confirmed_code_bytes=43,confirmed_instructions=13,
        independent_model_cases=196864,physical_bytes_preserved=True,full_patch_words_preserved=True,
        game_meaning_of_patch_pairs_proved=False,consumer_executed=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPatchSwapClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
