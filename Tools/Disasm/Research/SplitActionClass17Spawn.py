"""Выделение уже размеченного общего входа 60E8 из ракетной обёртки без изменения команд."""
import contextlib,hashlib,io,json,os,re,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from SourcePresentation import format_function,instructions
import ActionClass17SpawnFacts as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionClass17SpawnVerification')['total_cases']==66560
    functions,source_map,symbols,flow,modified,inventory=(read(n) for n in ('Functions','SourceMap','Symbols','ControlFlow','ModifiedCode','Inventory'))
    parent=next(f for f in functions if f['region']=='Action' and f['address']==0x60AE)
    assert parent['name']=='CreateMissileForTarget' and parent['end_offset']==0x382
    start,end=0x60E8,0x6145;offset=start-0x5DC3;old_end=parent['end_offset']
    name,description=facts.FUNCTIONS[start];new_path='Source/Action/'+name+'.asm';pending={}
    parent_path=ROOT/parent['path'];current=parent_path.read_text('utf-8')
    needle='                LD (@ActionMissileCreateState.InitParameter), A';assert current.count(needle)==1
    cut=current.index(needle);head=current[:cut].rstrip()
    # Перенос комментария сохранения параметра вместе с самой инструкцией в новый файл.
    line='                ; Обновление операнда инициализации Unknown13 перед поиском, запись сохраняется и при отказе по слотам.'
    assert head.endswith(line);head=head[:-len(line)].rstrip()
    head=head.replace('адреса 60AE..6144','адреса 60AE..60E7')
    head+='\n                ; JP @Action.'+name+'.Entry, продолжение в '+name+'.asm\n\n                endmodule\n                endmodule\n'
    parent['end_offset']=offset
    child=dict(parent,name=name,address=start,offset=offset,end_offset=old_end,path=new_path,description=description)
    functions.insert(functions.index(parent)+1,child)
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if start<=i['address']<end]
    lines=['                module Action','                module '+name,'                ; Документация [алгоритм и проверка](../../Docs/ActionClass17Spawn.md)',
        '                ; -----------------------------------------','                ; '+description,'                ; исходная запись 17, перенесённый код банка 5, адреса 60E8..6144']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',start]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for item in records:
        pc=item['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        operation=facts.name_operands('Action',start,item['operation'].replace(',',', '))
        label='Entry' if pc==start else facts.LOCAL.get(pc,'');line=((label+':').ljust(16) if label else ' '*16)+operation
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    tail=format_function('\n'.join(lines+['                endmodule','                endmodule'])+'\n')
    assert len(instructions(head))+len(instructions(tail))==len(instructions(current))
    pending[parent_path]=head.encode('utf-8');pending[ROOT/new_path]=tail.encode('utf-8')
    original=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    owner=next(p for p in source_map if p['path']==parent['path']);old_length=owner['length']
    owner.update(length=offset-owner['offset'],sha256=hashlib.sha256(original[owner['offset']:offset]).hexdigest())
    source_map.insert(source_map.index(owner)+1,dict(owner,offset=offset,length=old_end-offset,path=new_path,origin=start,
        sha256=hashlib.sha256(original[offset:old_end]).hexdigest()))
    assert owner['length']+old_end-offset==old_length
    symbols['Action.'+name+'.Entry']=start
    for pc,label in facts.LOCAL.items():
        old='Action.CreateMissileForTarget.'+label;assert symbols.pop(old)==pc;symbols['Action.'+name+'.'+label]=pc
    region['roots']=sorted(set(region['roots'])|{start})
    for item in modified:
        if item['region']=='Action' and start<=item['writer']<end:
            assert item['path']==parent['path'];item['path']=new_path
        if item.get('target_path')==parent['path'] and start<=item['target']<end:item['target_path']=new_path
    facts.qualify_mutations(modified,flow,functions,source_map)
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions))
    inventory['ranges_by_kind']['code']+=1
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('ControlFlow',flow),('ModifiedCode',modified),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                include "../Action/CreateMissileForTarget.asm"\n                ent';assert text.count(needle)==1
    replacement='                include "../Action/CreateMissileForTarget.asm"'.ljust(80)+'; (0) жёсткий порядок, последовательное исполнение\n                ent\n'
    replacement+='                assert $ == #'+format(offset,'04X')+'\n                disp #60E8\n'
    replacement+=('                include "../Action/'+name+'.asm"').ljust(80)+'; (1) жёсткий порядок, общий вход создания\n                ent'
    pending[path]=text.replace(needle,replacement).encode('utf-8')
    for filename,extra in (('Knowledge.py',"\nfrom ActionClass17SpawnFacts import FUNCTIONS as CLASS17_SPAWN_FUNCTIONS\nFUNCTIONS['Action'].update(CLASS17_SPAWN_FUNCTIONS)\n"),
                           ('Contracts.py',"\nfrom ActionClass17SpawnFacts import CONTRACTS as CLASS17_SPAWN_CONTRACTS\nCONTRACTS.update(CLASS17_SPAWN_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert 'from ActionClass17SpawnFacts' not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionMissileCreationFacts.py';text=path.read_text('utf-8');assert ",0x60F1:'InitializeSlot'" in text
    pending[path]=text.replace(",0x60F1:'InitializeSlot'",'').encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = class17_spawn_name_operands(region,function_address,operation)')
    text+="\nfrom ActionClass17SpawnFacts import name_operands as class17_spawn_name_operands\nDOCUMENTS['Action',0x60E8]=('ActionClass17Spawn','алгоритм и проверка')\nLABELS['Action',0x60F1]='InitializeSlot'\n"
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    extra="\nfrom ActionClass17SpawnFacts import COMMENTS as CLASS17_SPAWN_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(CLASS17_SPAWN_COMMENTS)\n"
    pending[path]=text.replace(needle,extra+needle).encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionClass17SpawnState' not in text
    block='\n                ; Существующий операнд общего создателя, память не выделяется\n                module ActionClass17SpawnState\n'
    block+=('InitialParam    equ #612E').ljust(80)+'; начальный Unknown13, записывается до поиска слота\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');needle=next(line for line in text.splitlines() if line.startswith('| #60AE | [Action.'))
    row='| #60E8 | [Action.'+name+'](../'+new_path+') | '+description+' |';text=text.replace(needle,needle+'\n'+row)
    count=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    pending[path]=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {count} | {described} |',text).encode('utf-8')
    for relative,extra in (('Docs/FunctionDetails/Action.md','\n## '+name+'\n\n[Общий создатель](../../'+new_path+'). [Алгоритм и точный договор](../ActionClass17Spawn.md).\n'),
                           ('Docs/ActionMissileCreation.md','\nОбщий дополнительный вход 60E8 выделен в [CreateClass17LinkedRecord](../Source/Action/CreateClass17LinkedRecord.asm). Его полный договор описан [отдельно](ActionClass17Spawn.md), ракетная обёртка заканчивается по 60E7 и продолжает исполнение в следующем файле.\n'),
                           ('Docs/ModifiedCode.md','\nПисатель 60E8 и операнд 612E теперь находятся в [CreateClass17LinkedRecord](../Source/Action/CreateClass17LinkedRecord.asm), физические адреса перенесённого банка 5 сохранены.\n')):
        path=ROOT/relative;pending[path]=(path.read_text('utf-8')+extra).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionClass17SpawnSplit';history=ROOT/'Tools/Disasm/Research/History/BeforeActionClass17SpawnSplit'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,a) for p,a in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='class17-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,additional_physical_fragments=1,confirmed_code_bytes=end-start,
        instruction_sequence_preserved=True,physical_bytes_preserved=True,model_cases=66560,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass17SpawnClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
