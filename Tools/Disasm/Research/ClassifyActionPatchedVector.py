"""Выделение проверенной переходной цепочки из UnknownAE73, без сборки."""
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionPatchedVectorFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionPatchedVectorVerification');assert proof['passed'] and proof['total_cases']==212236
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    source_map,symbols,inventory,functions,flow=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow')]
    parent=next(f for f in functions if f['region']=='Action' and f['address']==0xAE73)
    assert parent['semantic_status']=='unknown' and parent['end_offset']==0x4FF5
    old=next(i for i in source_map if i['path']==parent['path']);name,description=facts.FUNCTIONS[0xAF43]
    code_path='Source/Action/'+name+'.asm';pending={}
    renames={'Action.UnknownAE73.PointAF43':'Action.'+name+'.Entry','Action.UnknownAE73.PointAFEF':'Action.'+name+'.RestoreIX'}
    # Поиск только ссылок на два выделяемых входа, остальные ветви Unknown сохраняются.
    for folder,pattern in (('Source','*.asm'),('Source','*.inc')):
        for path in (ROOT/folder).rglob(pattern):
            if path==ROOT/parent['path']:continue
            before=path.read_text('utf-8');after=before
            for a,b in renames.items():after=after.replace(a,b)
            if after!=before:
                lines=after.splitlines()
                for i,line in enumerate(lines):
                    code,sep,note=line.partition(';')
                    if sep and code.strip():assert len(code.rstrip())<80;lines[i]=code.rstrip().ljust(80)+';'+note
                pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    for before,after in renames.items():assert after not in symbols;symbols[after]=symbols.pop(before)
    for address,label in facts.LOCAL.items():
        key='Action.'+name+'.'+label
        if key not in symbols:symbols[key]=address
        else:assert symbols[key]==address
    def piece(start,end,path,origin):return dict(slot=17,offset=start,length=end-start,kind='code',path=path,origin=origin,
        sha256=hashlib.sha256(source[start:end]).hexdigest())
    index=source_map.index(old);source_map[index:index+1]=[
        piece(0x4E73,0x4F43,parent['path'],0xAE73),piece(0x4F43,0x4FF5,code_path,0xAF43)]
    parent['end_offset']=0x4F43;function_index=functions.index(parent)+1
    functions.insert(function_index,dict(region='Action',name=name,address=0xAF43,slot=17,offset=0x4F43,
        description=description,semantic_status='described',end_offset=0x4FF5,path=code_path))
    region=next(r for r in flow if r['name']=='Action');region['roots']=sorted(set(region['roots'])|{0xAF43})
    records=[i for i in region['instructions'] if 0xAF43<=i['address']<0xAFF5]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x4F43:0x4FF5]
    validate_notes([region],{'Action':facts.COMMENTS})
    path=ROOT/parent['path'];text=path.read_text('utf-8');needle='PointAF43:      ';assert text.count(needle)==1
    prefix=text[:text.index(needle)].replace('#4E73..#4FF4','#4E73..#4F42')
    assert prefix.rstrip().endswith('RET');pending[path]=(prefix+'                endmodule\n                endmodule\n').encode('utf-8')
    lines=['                module Action','                module '+name,
        '                ; Документация [три компоненты и арифметический SP](../../Docs/ActionPatchedVector.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, общая RAM банка 2, адреса AF43..AFF4']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xAF43]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines+=['                ; -----------------------------------------']
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=facts.name_operands('Action',0xAF43,record['operation'].replace(',',', '));label='Entry' if pc==0xAF43 else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/code_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions))
    modified=read('ModifiedCode')
    for item in modified:
        if item['region']=='Action' and 0xAF43<=item['writer']<0xAFF5:item['path']=code_path
    for stem,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionPatchedVectorState' not in text
    block='\n                ; Разнесённые исходные операнды и выходы, память не выделяется\n                module ActionPatchedVectorState\n'
    for label,address in (*facts.INPUTS,*facts.OUTPUTS,('SavedIX',0xAFF1)):
        block+=label.ljust(16)+('equ #'+format(address,'04X')).ljust(64)+'; существующее слово переходного вычислителя\n'
    block+='                endmodule\n\n                ; Исходные байтовые коэффициенты ACTION банка 0\n                module ActionPatchedVectorCoeffs\n'
    for row,addresses in enumerate(facts.COEFFICIENTS):
        for column,address in enumerate(addresses):block+=('C'+str(row)+str(column)).ljust(16)+('equ #'+format(address,'04X')).ljust(64)+'; signed8, исходный 80 даёт нулевой модуль\n'
    block+='                endmodule\n\n';pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Source/Files/17_ACTION.inc';text=pending.get(path,path.read_bytes()).decode('utf-8')
    needle='                include "../Action/UnknownAE73.asm"';assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+'\n                include "../Action/ComputePatchedVector.asm"').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionPatchedVectorFacts import FUNCTIONS as ACTION_PATCHED_VECTOR_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_PATCHED_VECTOR_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionPatchedVectorFacts import CONTRACTS as ACTION_PATCHED_VECTOR_CONTRACTS\nCONTRACTS.update(ACTION_PATCHED_VECTOR_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_patched_vector_name_operands(region,function_address,operation)')
    text+="\nfrom ActionPatchedVectorFacts import name_operands as action_patched_vector_name_operands\nDOCUMENTS['Action',0xAF43]=('ActionPatchedVector','три компоненты и арифметический SP')\n"
    text+='LABELS.update('+repr({('Action',a):label for a,label in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionPatchedVectorFacts import COMMENTS as ACTION_PATCHED_VECTOR_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_PATCHED_VECTOR_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    following=functions[function_index+1];needle='| #'+format(following['address'],'04X')+' |';assert text.count(needle)==1
    pending[path]=text.replace(needle,'| #AF43 | [Action.'+name+'](../'+code_path+') | '+description+' |\n'+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');start=text.index('## UnknownAE73\n');end=text.find('\n## ',start+4);assert end>0
    section='## UnknownAE73\n\n[Action.UnknownAE73](../../Source/Action/UnknownAE73.asm)\n\nUnknown, оставшийся фрагмент AE73..AF42 ещё не разобран.\n\nВход `#AE73`, запись 17, смещения `#4E73..#4F42`.\n\nСохраняет неизвестный договор и записи AF14, AF2F. Вычислитель AF43 выделен отдельно, его выходы и чтения не относятся к этому оставшемуся фрагменту.\n\n'
    section+='## '+name+'\n\n[Action.'+name+'](../../'+code_path+')\n\n'+description+'.\n\n[Контракт, перенос, SP и модель](../ActionPatchedVector.md).\n'
    pending[path]=(text[:start]+section+text[end:]).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';text=path.read_text('utf-8');lines=text.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('| Action | #AF43 |'):lines[i]=line.replace('[UnknownAE73.asm](../Source/Action/UnknownAE73.asm)','[ComputePatchedVector.asm](../Source/Action/ComputePatchedVector.asm)')
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPatchedVector';history=ROOT/'Tools/Disasm/Research/History/BeforeActionPatchedVector';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание кандидата и проверка рабочей копии до замены, прежний Unknown-файл сохраняется на месте.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    report=dict(passed=True,described_functions=1,parent_unknown_preserved=True,original_instruction_sequence_preserved=True,
        physical_bytes_preserved=True,compositional_model_cases=212236,independent_complete_child_oracle=False,
        all_six_overflow_sites=True,arithmetic_sp_and_original_carry_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPatchedVectorClassification.json').write_bytes(encode(report));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
