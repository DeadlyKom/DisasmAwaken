"""Пакетное восстановление 12 входов и 12 состояний, полная проверка кандидата до замены."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import re
import shutil
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from ActionRandomStreamLayout import STREAMS
import ActionRandomClusterFacts as facts
from ActionFoldedRandomData import TABLES,render,parse


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionFoldedRandomVerification')
    assert proof['passed'] and proof['total_cases']==218383 and proof['original_stream_entries']==15
    functions,source_map,symbols,flow,inventory=map(read,('Functions','SourceMap','Symbols','ControlFlow','Inventory'))
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    new=[item for item in STREAMS if item[0]>=3];tables={t[2]:t for t in TABLES}
    starts={entry-0x6000:(index,entry,pointer) for index,entry,pointer in new}
    new_data={pointer-0x6000:tables[pointer-0x6000] for index,_,pointer in new}
    ranges=[i for i in source_map if i['slot']==17 and i['kind']=='unclassified' and
        any(i['offset']<=start<i['offset']+i['length'] for start in (*starts,*new_data))]
    assert len(ranges)==6 and sum(i['length'] for i in ranges)==120
    removed={ROOT/i['path']:(ROOT/i['path']).read_bytes() for i in ranges}
    assert all(data==source[i['offset']:i['offset']+i['length']] for i in ranges for path,data in removed.items() if path==ROOT/i['path'])
    pending={};new_functions=[];new_instructions=[];replacements={}
    for old in ranges:
        parts=[];cursor=old['offset'];end=cursor+old['length']
        while cursor<end:
            if cursor in starts:
                index,entry,pointer=starts[cursor];name,description=facts.FUNCTIONS[entry]
                path='Source/Action/'+name+'.asm';size=7;assert cursor+size<=end
                assert source[cursor:cursor+7]==bytes((0xD9,0x21,pointer&255,pointer>>8,0xC3,0x08,0xEC))
                function=dict(region='Action',name=name,address=entry,slot=17,offset=cursor,end_offset=cursor+7,
                    path=path,description=description,semantic_status='described')
                assert not any(f['region']=='Action' and f['address']==entry for f in functions)
                new_functions.append(function)
                lines=['                module Action','                module '+name,
                    '                ; Документация [генератор и все потоки](../../Docs/ActionFoldedRandom.md)',
                    '                ; -----------------------------------------','                ; '+description,
                    '                ; исходная запись 17, банк 0, смещения #'+format(cursor,'04X')+'..#'+format(cursor+6,'04X')]
                for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',entry]):
                    lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
                lines+=['                ; -----------------------------------------']
                for address,operation,blob in ((entry,'EXX',source[cursor:cursor+1]),
                    (entry+1,'LD HL,#'+format(pointer,'04X'),source[cursor+1:cursor+4]),
                    (entry+4,'JP #EC08',source[cursor+4:cursor+7])):
                    new_instructions.append(dict(address=address,operation=operation,hex=blob.hex(),slot=17,offset=address-0x6000))
                    before,_=facts.COMMENTS.get(address,([],None));lines+=['                ; '+v for v in before]
                    op=facts.name_operands('Action',entry,operation.replace(',',', '))
                    lines.append(('Entry:'.ljust(16) if address==entry else ' '*16)+op)
                lines+=['','                endmodule','                endmodule']
                pending[ROOT/path]=('\n'.join(lines)+'\n').encode('utf-8');kind='code';origin=entry
                key='Action.'+name+'.Entry';assert key not in symbols;symbols[key]=entry
            else:
                assert cursor in new_data,cursor
                table=new_data[cursor];path=table[1];size=3;origin=cursor+0x6000;kind='typed_data'
                text,bindings=render(source,table);assert parse(text,table)==(source[cursor:cursor+3],bindings)
                assert not set(bindings)&set(symbols);symbols.update(bindings);pending[ROOT/path]=text.encode('utf-8')
            parts.append(dict(slot=17,offset=cursor,length=size,kind=kind,path=path,origin=origin,
                sha256=hashlib.sha256(source[cursor:cursor+size]).hexdigest()));cursor+=size
        assert cursor==end
        replacements[old['path']]=parts
    assert len(new_functions)==12 and len(new_instructions)==36 and len(new_data)==12
    # Сохранение всех уже оформленных физических записей, их исходники не переписываются.
    baseline={ROOT/t[1]:(ROOT/t[1]).read_bytes() for t in TABLES if t[2] not in new_data}
    for table in TABLES:
        if table[2] not in new_data:assert parse(baseline[ROOT/table[1]].decode('utf-8'),table)[0]==source[table[2]:table[3]]
    final_map=[]
    for item in source_map:final_map+=replacements.get(item['path'],[item])
    for function in sorted(new_functions,key=lambda f:f['address']):
        at=next(i for i,f in enumerate(functions) if f['region']=='Action' and f['address']>function['address'])
        functions.insert(at,function)
    region=next(r for r in flow if r['name']=='Action')
    assert not any(i['address'] in {v['address'] for v in new_instructions} for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+new_instructions,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS))
    region['branches']=sorted(set(region['branches'])|{0xEC08})
    region['instruction_count']+=36;region['code_bytes']+=84;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+36)
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in final_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in final_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('Functions',functions),('SourceMap',final_map),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    for old in ranges:
        needle='                incbin "../Resources/17_ACTION/'+(ROOT/old['path']).name+'"';assert text.count(needle)==1
        lines=[]
        for part in replacements[old['path']]:
            target=part['path'].removeprefix('Source/')
            lines+=['                assert $ == #'+format(part['offset'],'04X'),'                disp #'+format(part['origin'],'04X'),
                '                include "../'+target+'"','                ent']
        text=text.replace(needle,'\n'.join(lines))
    pending[path]=text.encode('utf-8')
    # Именование только доказанных прямых целей и актуализация числа проверенных сценариев в старых заголовках.
    for path in (ROOT/'Source/Action').glob('*.asm'):
        before=path.read_text('utf-8');lines=[]
        for line in before.splitlines():
            if line.strip() and not line.lstrip().startswith(';'):
                code,sep,note=line.partition(';')
                code=code[:16]+facts.name_operands('Action',-1,code[16:])
                line=code.rstrip().ljust(80)+';'+note if sep else code
            line=line.replace('203011','218383').replace('все четыре входа','ядро и все пятнадцать внешних входов')
            line=line.replace('три внешних входа','пятнадцать внешних входов').replace('три исходных состояния','пятнадцать исходных состояний')
            lines.append(line)
        after='\n'.join(lines)+'\n'
        if after!=before:pending[path]=after.encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionRandomClusterFacts import FUNCTIONS as ACTION_RANDOM_CLUSTER_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_RANDOM_CLUSTER_FUNCTIONS)\n"),
        ('Contracts.py','\nfrom ActionRandomClusterFacts import CONTRACTS as ACTION_RANDOM_CLUSTER_CONTRACTS\nCONTRACTS.update(ACTION_RANDOM_CLUSTER_CONTRACTS)\n')):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text
        pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    anchor='def name_operands(region, function_address, operation):';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    operation = action_random_cluster_name_operands(region, function_address, operation)')
    text+='\nfrom ActionRandomClusterFacts import name_operands as action_random_cluster_name_operands\n'
    text+='DOCUMENTS.update({("Action",a): ("ActionFoldedRandom", "генератор и все потоки") for a in '+repr(tuple(facts.FUNCTIONS))+'})\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');anchor='\n\nif __name__ == "__main__":';assert text.count(anchor)==1
    pending[path]=text.replace(anchor,"\nfrom ActionRandomClusterFacts import COMMENTS as ACTION_RANDOM_CLUSTER_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_RANDOM_CLUSTER_COMMENTS)\n"+anchor).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8')
    text=re.sub(r'\| Action \| \d+ \| \d+ \|', '| Action | '+str(sum(f['region']=='Action' for f in functions))+' | '+str(sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions))+' |',text)
    details=(ROOT/'Docs/FunctionDetails/Action.md').read_text('utf-8')
    for f in sorted(new_functions,key=lambda f:f['address'],reverse=True):
        following=next(v for v in functions if v['region']=='Action' and v['address']>f['address'])
        needle='| #'+format(following['address'],'04X')+' | [Action.'+following['name']+']';assert text.count(needle)==1
        row='| #'+format(f['address'],'04X')+' | [Action.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n'
        text=text.replace(needle,row+needle)
        needle='## '+following['name']+'\n';assert details.count(needle)==1
        section='## '+f['name']+'\n\n[Action.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Алгоритм и полный договор](../ActionFoldedRandom.md).\n\n'
        details=details.replace(needle,section+needle)
    pending[path]=text.encode('utf-8');pending[ROOT/'Docs/FunctionDetails/Action.md']=details.encode('utf-8')
    path=ROOT/'Docs/ActionFoldedRandom.md';text=path.read_text('utf-8')
    start=text.index('[Общее ядро]');end=text.index('\n## Физические записи')
    text=text[:start]+'[Общее ядро](../Source/Action/StepFoldedRandom.asm) и 15 внешних входов относятся к ACTION банка 0. Каждый вход выполняет EXX, выбирает собственную трёхбайтовую запись и входит в общее ядро. Ядро обновляет запись и возвращает новое слово в основной HL, обратный EXX восстанавливает DE и BC вызывающего.\n'+text[end:]
    start=text.index('| Поток |');end=text.index('\n## Точная рекурсия')
    table=['| Поток | Вход | Физический экземпляр | Адрес состояния | Начальный LowWord | FoldByte |','| --- | --- | --- | --- | --- | --- |']
    for index,entry,pointer in STREAMS:
        word=int.from_bytes(source[pointer-0x6000:pointer-0x6000+2],'little');fold=source[pointer-0x6000+2]
        table.append('| '+str(index)+' | [NextRandomWord'+str(index)+'](../Source/Action/NextRandomWord'+str(index)+'.asm), '+format(entry,'04X')+' | [Stream'+str(index)+'](../Source/Action/Data/FoldRandomStream'+str(index)+'.asm) | '+format(pointer,'04X')+' | '+str(word)+' | '+str(fold)+' |')
    text=text[:start]+'\n'.join(table)+'\n\nВсе 45 байтов состояний EBDB..EC07 оформлены физическими экземплярами STRUCT. Восстановлены все 105 байтов пятнадцати входов EB72..EBDA, включая 84 байта, ранее остававшиеся в бинарных участках. Соседние исходные байты вне этого блока не изменялись. Высокоуровневые игровые роли потоков ещё не названы, распределение, период и вероятности проверок вызывающего кода не доказаны.\n'+text[end:]
    text=text.replace('203011','218383').replace('все три внешних входа','все пятнадцать внешних входов')
    pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/DataFormats.md';text=path.read_text('utf-8')
    old=next(line for line in text.splitlines() if line.startswith('Три физических `FFoldedRandomState`'))
    new_line='Пятнадцать физических `FFoldedRandomState` по три байта занимают EBDB..EC07, всего 45 исходных байтов. LowWord по смещениям 0..1 и FoldByte по смещению 2 являются числовым состоянием. Все экземпляры, исходные значения, входы и ограничения приведены в [ActionFoldedRandom](ActionFoldedRandom.md).'
    pending[path]=text.replace(old,new_line).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/GenerateDocs.py';text=path.read_text('utf-8')
    text=text.replace('три физических LowWord и FoldByte','15 физических экземпляров LowWord и FoldByte, 45 байтов')
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRandomCluster';history=ROOT/'Tools/Disasm/Research/History/BeforeActionRandomCluster'
    assert not candidate.exists() and not history.exists()
    plan=[(path,path.read_bytes() if path.exists() else None,data) for path,data in pending.items()]
    for path,before,data in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Дополнение кандидата только входами статических проверок, без копирования History и других кандидатов.
    for directory in ('Source','Includes','Builder','Docs','Tools/Disasm/Disk','Tools/Disasm/Extracted','Tools/Disasm/Reports'):
        for path in (ROOT/directory).rglob('*'):
            if not path.is_file() or path in removed:continue
            target=candidate/path.relative_to(ROOT)
            if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    import VerifySources,CheckSourceLabels,CheckDocumentation,CheckFilePlacement,AuditConformance
    modules=(VerifySources,CheckSourceLabels,CheckDocumentation,CheckFilePlacement,AuditConformance);roots=[m.ROOT for m in modules]
    try:
        for module in modules:module.ROOT=candidate
        with contextlib.redirect_stdout(io.StringIO()):VerifySources.main();CheckSourceLabels.main()
        for module in (CheckDocumentation,CheckFilePlacement):assert module.audit()['passed']
        audit=AuditConformance.audit()
        for key in ('unlinked_functions','missing_includes_or_resources','missing_include_order','unresolved_global_references',
            'duplicate_global_definitions','global_reference_case_mismatches','source_files_outside_graph','python_duplicate_literal_keys'):
            assert not audit[key],(key,audit[key])
    finally:
        for module,root in zip(modules,roots):module.ROOT=root
    # Проверка всех исходных контрольных точек после проверки кандидата и до первой замены.
    for path,before in baseline.items():assert path.read_bytes()==before
    for path,before,data in plan:assert (path.read_bytes() if path.exists() else None)==before
    for path,before in removed.items():assert path.read_bytes()==before
    for path,before in {**{p:b for p,b,_ in plan if b is not None},**removed}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,data in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённых шести ресурсов после сверки и сохранения исходных копий.
    for path,before in removed.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
        assert path.read_bytes()==before==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
    report=dict(passed=True,new_functions=12,total_stream_functions=15,shared_core_functions=1,
        new_code_bytes=84,new_instructions=36,new_typed_bytes=36,total_typed_state_bytes=45,
        original_bytes_preserved=True,model_cases=218383,full_candidate_checked_before_publication=True,
        original_three_physical_sources_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionRandomClusterClassification.json').write_bytes(encode(report))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
