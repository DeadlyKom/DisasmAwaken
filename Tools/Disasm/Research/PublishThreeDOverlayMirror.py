"""Защищённая публикация одного совпадающего оверлея, массовый ExportSources не запускается."""
from collections import Counter
import contextlib,copy,hashlib,io,json,re,shutil
from ClassifyControlsTextDisplay import ROOT
from Contracts import CONTRACTS
from ExportSources import REGION_COMMENTS
from VerifySources import main as verify
from ThreeDOverlayData import NAMES as DATA_NAMES,TABLES as DATA_TABLES,render as render_data


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('ThreeDOverlayMirrorVerification');assert proof['passed'] and proof['byte_identical']
    with contextlib.redirect_stdout(io.StringIO()):verify()
    old_functions,old_map,symbols,flow,inventory,mutations=[read(n) for n in ('Functions','SourceMap','Symbols','ControlFlow','Inventory','ModifiedCode')]
    primary=[f for f in old_functions if f['region']=='Action' and 0xC000<=f['address']<0xE020]
    previous=[f for f in old_functions if f['region']=='ThreeD']
    assert len(primary)==122 and len(previous)==98
    baseline={ROOT/f['path']:(ROOT/f['path']).read_bytes() for f in (*primary,*previous)}
    original=(ROOT/'Tools/Disasm/Extracted/Active/19_3DPART.C.sectors.bin').read_bytes()
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert original[:8224]==source[0x6000:0x8020] and len(original)==8448
    code_names={key:'ThreeD.'+key.removeprefix('Action.') for key,value in symbols.items() if key.startswith('Action.') and 0xC000<=value<0xE020}
    for old,new in DATA_NAMES.items():
        code_names.update({key:new+key[len(old):] for key in symbols if key.startswith(old+'.')})
    token=re.compile(r'\b(?:Action(?:\.[A-Za-z_][A-Za-z0-9_]*)+|'+
                     '|'.join(re.escape(name)+r'(?:\.[A-Za-z_][A-Za-z0-9_]*)+' for name in DATA_NAMES)+r')\b')
    def convert(text):
        return token.sub(lambda match:code_names.get(match[0],match[0]),text)
    new_functions=[];pending={};path_map={}
    context_notes=['дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F',
        'перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла',
        'нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения']
    for function in primary:
        new=dict(function,region='ThreeD',slot=19,offset=function['offset']-0x6000,end_offset=function['end_offset']-0x6000,
                 path='Source/ThreeD/'+function['name']+'.asm')
        new_functions.append(new);path_map[function['path']]=new['path']
        text=baseline[ROOT/function['path']].decode('utf-8').replace('\r\n','\n')
        text,count=re.subn(r'(?m)^(\s*module )Action$',r'\1ThreeD',text);assert count==1
        text=convert(text)
        text=re.sub(r'\]\((?:\.\./)+Docs/[^)]+\.md\)','](../../Docs/ThreeDOverlayMirror.md)',text)
        text=re.sub(r'\bACTION\b','3DPART',text)
        text,count=re.subn(r'(?m)^\s*; исходная запись 17[^\n]*',
            '                ; исходная запись 19, банк 0, смещения #'+format(new['offset'],'04X')+'..#'+format(new['end_offset']-1,'04X'),text)
        assert count==1
        text,count=re.subn(r'(?m)^(\s*; Note:)\n',lambda match:match[0]+''.join('                ;   '+note+'\n' for note in context_notes),text)
        assert count==1
        lines=['                '+line.lstrip() if line.lstrip().startswith(';') else line for line in text.splitlines()]
        pending[ROOT/new['path']]=('\n'.join(lines)+'\n').encode('utf-8')
    primary_pieces=[p for p in old_map if p['slot']==17 and 0x6000<=p['offset']<0x8020]
    assert sum(p['length'] for p in primary_pieces)==8224
    new_pieces=[]
    for piece in primary_pieces:
        start=piece['offset']-0x6000;end=start+piece['length']
        if piece['kind']=='code':path=path_map[piece['path']]
        elif piece['kind']=='typed_data':
            path='Source/ThreeD/Data/'+piece['path'].rsplit('/',1)[-1]
            text,names=render_data(original,path);pending[ROOT/path]=text.encode('utf-8')
            for key,value in names.items():assert key not in symbols;symbols[key]=value
        else:
            assert piece['kind']=='unclassified'
            path='Source/Resources/19_3DPART/Physical'+format(start,'04X')+'.bin'
            pending[ROOT/path]=original[start:end]
        new_pieces.append(dict(piece,slot=19,offset=start,path=path,sha256=hashlib.sha256(original[start:end]).hexdigest()))
    tail='Source/Resources/19_3DPART/SectorTail.bin';pending[ROOT/tail]=original[8224:]
    new_pieces.append(dict(slot=19,offset=8224,length=224,kind='unclassified',path=tail,origin=None,
                           sha256=hashlib.sha256(original[8224:]).hexdigest()))
    # Сохранение имён только доказанных входов и полей новой копии, общие внешние адреса остаются ACTION.
    for key in list(symbols):
        if key.startswith('ThreeD.'):del symbols[key]
    for key,new in code_names.items():
        if key.startswith('Action.'):
            assert new not in symbols;symbols[new]=symbols[key]
    first=min(i for i,f in enumerate(old_functions) if f['region']=='ThreeD')
    functions=[f for f in old_functions if f['region']!='ThreeD'];functions[first:first]=new_functions
    source_map=[item for item in old_map if item['slot']!=19]+new_pieces
    source_map.sort(key=lambda item:(item['slot'],item['offset']))
    primary_flow=next(r for r in flow if r['name']=='Action');mirror=next(r for r in flow if r['name']=='ThreeD')
    instructions=[dict(item,slot=19,offset=item['offset']-0x6000) for item in primary_flow['instructions'] if item['slot']==17 and 0x6000<=item['offset']<0x8020]
    assert sum(len(bytes.fromhex(item['hex'])) for item in instructions)==sum(p['length'] for p in new_pieces if p['kind']=='code')
    pcs={item['address'] for item in instructions};calls=set();branches=set();external=[]
    for item in instructions:
        match=re.match(r'^(CALL|JP|JR|DJNZ) .*#([0-9A-F]{4})$',item['operation'])
        if match:
            target=int(match[2],16);(calls if match[1]=='CALL' else branches).add(target)
            if not 0xC000<=target<0xE020:external.append(dict(address=item['address'],operation=item['operation'],target=target))
    mirror.update(instructions=instructions,instruction_count=len(instructions),code_bytes=sum(len(bytes.fromhex(i['hex'])) for i in instructions),
        roots=sorted({f['address'] for f in new_functions}),calls=sorted(calls),branches=sorted(branches),overlaps=[],
        unresolved=[copy.deepcopy(i) for i in primary_flow['unresolved'] if i['address'] in pcs],
        mirror_source_region='Action',mirror_logical_bytes=8224,external_resident_dependencies=external)
    mirror['classified_fraction']=mirror['code_bytes']/mirror['total_bytes']
    # Замена только строк трёхмерной копии в реестре самомодификации.
    mutations=[m for m in mutations if m['region']!='ThreeD']
    for item in list(mutations):
        if item['region']!='Action' or not 0xC000<=item['writer']<0xE020:continue
        new=copy.deepcopy(item);new['region']='ThreeD'
        owner=next(f for f in new_functions if f['address']<=item['writer']<f['address']+f['end_offset']-f['offset'])
        new['path']=owner['path'];new.update(writer_slot=19,writer_offset=item['writer']-0xC000,writer_bank=0)
        if 0xC000<=item['target']<0xE020 and item.get('target_bank',0)==0:
            new.update(target_region='ThreeD',target_slot=19,target_offset=item['target']-0xC000,target_bank=0)
            target_owner=next((f for f in new_functions if f['address']<=item['target']<f['address']+f['end_offset']-f['offset']),None)
            if target_owner:new['target_path']=target_owner['path']
        mutations.append(new)
    mutations.sort(key=lambda item:(item['region'],item['writer'],item['target']))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),
                     unknown=sum(f['semantic_status']!='described' for f in functions),instructions=sum(r['instruction_count'] for r in flow))
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(p['length'] for p in source_map if p['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('ControlFlow',flow),('Inventory',inventory),('ModifiedCode',mutations)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    # Полная физическая последовательность слота 19, секторный хвост остаётся отдельным неизменённым ресурсом.
    unit=['; -----------------------------------------','; запись 19, 3DPART.C','; логическая длина 8224, полный секторный размер 8448','; -----------------------------------------']
    original_unit=(ROOT/'Source/Files/17_ACTION.inc').read_text('utf-8')
    order={}
    for line in original_unit.splitlines():
        match=re.search(r'include "../Action/([^"/]+\.asm)".*;(.*)',line)
        if match and 'жёсткий порядок' in match[2]:order[match[1]]=match[2].strip()
    for piece in new_pieces:
        unit.append('                assert $ == #'+format(piece['offset'],'04X'))
        if piece['kind'] in ('code','typed_data'):
            unit.append('                disp #'+format(piece['origin'],'04X'))
            line='                include "../'+piece['path'].removeprefix('Source/')+'"'
            if piece['path'].rsplit('/',1)[-1] in order:line=line.ljust(80)+'; '+order[piece['path'].rsplit('/',1)[-1]]
            unit.extend((line,'                ent'))
        else:
            unit.extend(('                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей',
                         '                incbin "../'+piece['path'].removeprefix('Source/')+'"'))
    unit.append('                assert $ == #2100');pending[ROOT/'Source/Files/19_3DPART.inc']=('\n'.join(unit)+'\n').encode('utf-8')
    contracts={('ThreeD',f['address']):tuple([[convert(v) for v in group] for group in CONTRACTS['Action',f['address']]][:3]+[[*context_notes,*[convert(v) for v in CONTRACTS['Action',f['address']][3]]]]) for f in primary if ('Action',f['address']) in CONTRACTS}
    labels={('ThreeD',address):name.rsplit('.',1)[-1] for name,address in symbols.items() if name.startswith('ThreeD.') and not name.endswith('.Entry')}
    comments={pc:([convert(v) for v in before],convert(right) if right else right) for pc,(before,right) in REGION_COMMENTS.get('Action',{}).items() if pc in pcs}
    facts='"""Побайтовая копия слота 19, внешнее состояние и банк 0 являются условиями переноса доказательств."""\n'
    for name,value in (('FUNCTIONS',{f['address']:(f['name'],f['description']) for f in new_functions}),('CONTRACTS',contracts),('LABELS',labels),
        ('COMMENTS',comments),('CODE_NAMES',code_names),('CODE_RANGES',tuple((f['address'],f['address']+f['end_offset']-f['offset']) for f in new_functions))):
        facts+=name+' = '+repr(value)+'\n\n'
    facts+='def name_operands(region,address,operation):\n    if region=="ThreeD":\n        from SemanticNames import name_operands as primary_names\n        operation=primary_names("Action",address,operation)\n        import re\n        operation=re.sub(r"(?<=@)[A-Za-z_][A-Za-z0-9_.]*",lambda m:CODE_NAMES.get(m[0],m[0]),operation)\n    return operation\n'
    pending[ROOT/'Tools/Disasm/Research/ThreeDOverlayMirrorFacts.py']=facts.encode('utf-8')
    for filename,extra in (
        ('Knowledge.py','\nfrom ThreeDOverlayMirrorFacts import FUNCTIONS as THREED_OVERLAY_FUNCTIONS\nFUNCTIONS["ThreeD"]=dict(THREED_OVERLAY_FUNCTIONS)\n'),
        ('Contracts.py','\nfrom ThreeDOverlayMirrorFacts import CONTRACTS as THREED_OVERLAY_CONTRACTS\nCONTRACTS.update(THREED_OVERLAY_CONTRACTS)\n'),
        ('ExportSources.py','\nfrom ThreeDOverlayMirrorFacts import COMMENTS as THREED_OVERLAY_COMMENTS\nREGION_COMMENTS["ThreeD"]=dict(THREED_OVERLAY_COMMENTS)\n')):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert 'from ThreeDOverlayMirrorFacts import' not in text
        if filename=='ExportSources.py':
            needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1;text=text.replace(needle,extra+needle)
        else:text+=extra
        pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = three_d_overlay_names(region, function_address, operation)')
    text+='\nfrom ThreeDOverlayMirrorFacts import LABELS as THREED_OVERLAY_LABELS,name_operands as three_d_overlay_names\nLABELS.update(THREED_OVERLAY_LABELS)\nDOCUMENTS.update({("ThreeD",a):("ThreeDOverlayMirror","копия и границы доказательства") for a in '+repr(tuple(f['address'] for f in new_functions))+'})\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/Analyze.py';text=path.read_text('utf-8')
    needle='from Knowledge import FUNCTIONS';assert text.count(needle)==1
    text=text.replace(needle,needle+'\nfrom ThreeDOverlayMirrorFacts import CODE_RANGES as THREED_OVERLAY_CODE_RANGES')
    needle='"ThreeD": ((0xC000, 0xCEE3), (0xCF08, 0xCF0B), (0xD10A, 0xD194))';assert text.count(needle)==1
    pending[path]=text.replace(needle,'"ThreeD": THREED_OVERLAY_CODE_RANGES').encode('utf-8')
    # Документация новой копии с обратными ссылками на каждый исходник и ссылками на первичные доказательства.
    rows=['# Точная копия 3DPART','',
        'Логические 8224 байта записи 19 полностью совпадают с ACTION, смещения 6000..801F. Секторный хвост 224 байта сохранён отдельно. [Проверка](../Tools/Disasm/Research/CheckThreeDOverlayMirror.py) сравнивает фактические байты и проверяет отсутствие непонятных ручных комментариев до публикации.',
        '', '121 контракт перенесён только при одинаковых внешней RAM, загруженном банке 0 и состояниях входа. Общие внешние процедуры вне файла сохраняют ссылки ACTION. Самостоятельная нативная загрузка 3DPART не выполнялась. [Исходная разметка и прежние частичные контракты](../Tools/Disasm/Reports/ThreeDOverlayMirrorVerification.json) сохранены, неоднозначность CF08 остаётся Unknown.',
        '', 'Поля RAM и константы из Includes общие для одинакового адресного пространства. Четыре физических блока этой копии имеют отдельные метки ThreeDClipPoints, ThreeDClipProductsData и ThreeDLineMasks. Новые адреса и области памяти не выделяются.',
        '', '## Процедуры', '', '| Адрес | Копия | Первичный разбор |', '| --- | --- | --- |']
    for function,primary_function in zip(new_functions,primary):
        rows.append('| '+format(function['address'],'04X')+' | ['+function['name']+'](../'+function['path']+') | ['+primary_function['name']+'](../'+primary_function['path']+') |')
    rows.extend(('', '## Физические записи', ''))
    rows.extend('- ['+path.rsplit('/',1)[-1]+'](../'+path+')' for path,start,end in DATA_TABLES)
    rows.extend(('', 'Код, входы, данные, таблицы переходов и самомодификация совпадают побайтово. Перенос математики не заменяет проверку всех игровых состояний и всех внешних данных. R/T и IRQ ограничены первичными договорами. Сборка и нативный игровой процесс в этой работе не выполнялись.', ''))
    pending[ROOT/'Docs/ThreeDOverlayMirror.md']='\n'.join(rows).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8')
    text=re.sub(r'\| ThreeD \| \d+ \| \d+ \|','| ThreeD | 122 | 121 |',text)
    lines=text.splitlines();positions=[i for i,line in enumerate(lines) if line.startswith('| #') and '[ThreeD.' in line]
    assert len(positions)==98 and positions==list(range(positions[0],positions[-1]+1))
    lines[positions[0]:positions[-1]+1]=['| #'+format(f['address'],'04X')+' | [ThreeD.'+f['name']+'](../'+f['path']+') | '+f['description']+' |' for f in new_functions]
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    details=['# ThreeD','', '[Контекст копии и границы доказательства](../ThreeDOverlayMirror.md).','']
    for function in new_functions:
        details.extend(('## '+function['name'],'','[ThreeD.'+function['name']+'](../../'+function['path']+')','',function['description']+'.',''))
    pending[ROOT/'Docs/FunctionDetails/ThreeD.md']='\n'.join(details).encode('utf-8')
    path=ROOT/'Docs/ModifiedCode.md';lines=[]
    for line in path.read_text('utf-8').splitlines():
        if line.startswith('| ThreeD |'):continue
        lines.append(line)
    index=next(i for i,line in enumerate(lines) if line.startswith('| Controls |'))
    mirror_rows=['| ThreeD | #'+format(m['writer'],'04X')+' | #'+format(m['target'],'04X')+' | `'+m['target_operation']+'` | ['+m['path'].rsplit('/',1)[-1]+'](../'+m['path']+') |' for m in mutations if m['region']=='ThreeD']
    lines[index:index]=mirror_rows;pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    # Обновление оставшихся ссылок документации на переименованные файлы, без изменения посторонних разделов.
    old_paths={f['path']:next(n['path'] for n in new_functions if n['address']<=f['address']<n['address']+n['end_offset']-n['offset']) for f in previous}
    for path in (ROOT/'Docs').rglob('*.md'):
        before=pending.get(path,path.read_bytes()).decode('utf-8');after=before
        for old,new in old_paths.items():after=after.replace(old,new)
        if after!=before:pending[path]=after.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ThreeDOverlayMirror';history=ROOT/'Tools/Disasm/Research/History/BeforeThreeDOverlayMirror'
    assert not candidate.exists() and not history.exists()
    removed={ROOT/p['path']:(ROOT/p['path']).read_bytes() for p in old_map if p['slot']==19 and ROOT/p['path'] not in pending}
    # Создание кандидата и сравнение всего прочитанного состояния до первой замены.
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for path,before,data in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Дополнение только входами статических проверок, Research/History и другие кандидаты не копируются.
    for directory in ('Source','Includes','Builder','Docs','Tools/Disasm/Disk','Tools/Disasm/Extracted','Tools/Disasm/Reports'):
        for path in (ROOT/directory).rglob('*'):
            if not path.is_file() or path in removed:continue
            target=candidate/path.relative_to(ROOT)
            if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    # Проверка всего кандидата до изменения рабочей копии, все отчёты пишутся только внутри кандидата.
    import VerifySources,CheckSourceLabels,CheckDocumentation,CheckFilePlacement,AuditConformance
    modules=(VerifySources,CheckSourceLabels,CheckDocumentation,CheckFilePlacement,AuditConformance)
    roots=[module.ROOT for module in modules]
    try:
        for module in modules:module.ROOT=candidate
        with contextlib.redirect_stdout(io.StringIO()):
            VerifySources.main();CheckSourceLabels.main()
        for module,stem in ((CheckDocumentation,'DocumentationVerification'),(CheckFilePlacement,'FilePlacementVerification')):
            report=module.audit();assert report['passed'],report
            (candidate/('Tools/Disasm/Reports/'+stem+'.json')).write_bytes(encode(report))
        audit=AuditConformance.audit()
        for key in ('unlinked_functions','missing_includes_or_resources','missing_include_order','unresolved_global_references',
                    'duplicate_global_definitions','global_reference_case_mismatches','source_files_outside_graph','python_duplicate_literal_keys'):
            assert not audit[key],(key,audit[key])
        (candidate/'Tools/Disasm/Reports/ConformanceAudit.json').write_bytes(encode(audit))
    finally:
        for module,root in zip(modules,roots):module.ROOT=root
    for path,before in baseline.items():assert path.read_bytes()==before
    for path,before,data in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in removed.items():assert path.read_bytes()==before
    for path,before in {**{p:b for p,b,data in plan if b is not None},**removed}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,data in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только полностью заменённых файлов после сохранения и проверки исходных физических байтов.
    for path,before in removed.items():
        assert path.resolve().is_relative_to((ROOT/'Source/ThreeD').resolve()) or path.resolve().is_relative_to((ROOT/'Source/Resources/19_3DPART').resolve())
        assert path.read_bytes()==before==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
    result=dict(passed=True,original_logical_bytes_preserved=8224,sector_tail_bytes_preserved=224,
        source_functions=122,described=121,unknown=1,typed_bytes=42,
        native_loading_executed=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ThreeDOverlayMirrorClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
