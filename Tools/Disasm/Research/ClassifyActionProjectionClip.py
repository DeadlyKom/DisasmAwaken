"""Публикация граничного отбора и его физической таблицы, неизвестный префикс сохраняется."""
from collections import Counter
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionProjectionClipFacts as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionProjectionClipVerification');assert proof['passed'] and proof['total_cases']==267008
    functions,source_map,symbols,inventory,flow,modified=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    old=next(f for f in functions if f['region']=='Action' and f['address']==0xE1D1)
    assert (old['name'],old['end_offset'])==('UnknownE1D1',0x8299)
    path=ROOT/old['path'];old_text=path.read_text('utf-8');old_range=next(i for i in source_map if i['path']==old['path'])
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();pending={}
    name,description=facts.FUNCTIONS[0xE213];new_path='Source/Action/'+name+'.asm'
    first=dict(old,end_offset=0x8213)
    second=dict(old,name=name,address=0xE213,offset=0x8213,path=new_path,description=description,semantic_status='described')
    renames={}
    for key,value in symbols.items():
        if key.startswith('Action.UnknownE1D1.') and value>=0xE213:
            assert value in facts.LOCAL,(key,value);renames[key]='Action.'+name+'.'+facts.LOCAL[value]
    def rename(text):
        for before,after in renames.items():text=re.sub(r'\b'+re.escape(before)+r'\b',after,text)
        return text
    # Поиск только ссылок на переносимые метки, окружающие пользовательские исходники сохраняются.
    for pattern in ('*.asm','*.inc'):
        for current in (ROOT/'Source').rglob(pattern):
            if current==path:continue
            text=current.read_text('utf-8');after=rename(text)
            if text!=after:pending[current]=after.encode('utf-8')
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if 0xE213<=i['address']<0xE299]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x8213:0x8299]
    validate_notes([region],{'Action':facts.COMMENTS})
    lines=['                module Action','                module '+name,
        '                ; Документация [граничный отбор и таблица](../../Docs/ActionProjectionClip.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, код ACTION банка 0, адреса E213..E298']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xE213]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=record['operation'].replace(',',', ')
        for address,label in facts.LOCAL.items():op=op.replace('#'+format(address,'04X'),'@Action.'+name+'.'+label)
        op=op.replace('#E0E2','@Action.UnknownE020.PointE0E2').replace('#E40F','@Action.UnknownE36A.PointE40F')
        op=facts.name_operands('Action',0xE213,op);label='Entry' if pc==0xE213 else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule']
    continuation=dict(region='Action',name='PrepareProjectedBounds',path='Source/Action/PrepareProjectedBounds.asm')
    pending[ROOT/new_path]=format_function('\n'.join(lines)+'\n',continuation).encode('utf-8')
    # Сохранение неизвестного префикса текстом рабочей копии, без механического переоформления.
    cut=old_text.index('                LD HL, (#D7A2)\n');prefix=rename(old_text[:cut]).replace('E1D1..E298','E1D1..E212')
    prefix+='                endmodule\n                endmodule\n';pending[path]=format_function(prefix,second).encode('utf-8')
    index=functions.index(old);functions[index:index+1]=[first,second]
    index=source_map.index(old_range);ranges=[]
    for f in (first,second):
        start,end=f['offset'],f['end_offset'];ranges.append(dict(old_range,offset=start,length=end-start,path=f['path'],origin=f['address'],sha256=hashlib.sha256(source[start:end]).hexdigest()))
    source_map[index:index+1]=ranges
    symbols={renames.get(k,k):v for k,v in symbols.items()};assert 'Action.'+name+'.Entry' not in symbols
    symbols['Action.'+name+'.Entry']=0xE213;region['roots']=sorted(set(region['roots'])|{0xE213})
    for item in modified:
        if item['path']==old['path'] and item['writer']>=0xE213:item['path']=new_path
    # Выделение только 256 подтверждённых отсчётов, остальная часть бинарного ресурса сохраняется.
    data_range=next(i for i in source_map if i['slot']==17 and i['offset']<=0x3800<i['offset']+i['length'])
    assert data_range['offset']+data_range['length']==0x3900 and data_range['kind']=='unclassified'
    data_path=ROOT/data_range['path'];assert data_path.read_bytes()==source[data_range['offset']:0x3900]
    data_text,labels=facts.render(source);assert facts.parse(data_text)==(source[0x3800:0x3900],labels)
    assert not set(labels)&set(symbols);symbols.update(labels);pending[ROOT/facts.TABLE[1]]=data_text.encode('utf-8')
    pending[data_path]=source[data_range['offset']:0x3800]
    data_prefix=dict(data_range,length=0x3800-data_range['offset'],sha256=hashlib.sha256(pending[data_path]).hexdigest())
    typed=dict(slot=17,offset=0x3800,length=256,kind='typed_data',path=facts.TABLE[1],origin=0x9800,sha256=hashlib.sha256(source[0x3800:0x3900]).hexdigest())
    index=source_map.index(data_range);source_map[index:index+1]=[data_prefix,typed]
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']!='described' for f in functions))
    inventory['ranges_by_kind']=dict(Counter(i['kind'] for i in source_map))
    inventory['physical_bytes_by_kind']={kind:sum(i['length'] for i in source_map if i['kind']==kind) for kind in inventory['ranges_by_kind']}
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=pending.get(path,path.read_bytes()).decode('utf-8')
    line=next(l for l in text.splitlines() if 'include "../Action/UnknownE1D1.asm"' in l)
    repl=line+'\n                ent\n                assert $ == #8213\n                disp #E213\n'
    repl+=('                include "../Action/'+name+'.asm"').ljust(80)+'; (3) жёсткий порядок продолжения E020'
    text=text.replace(line,repl)
    for filename,before,after in (('PrepareProjectedBounds.asm','(3)','(4)'),('CaptureProjectedRecord.asm','(4)','(5)'),('UnknownE36A.asm','(5)','(6)')):
        line=next(l for l in text.splitlines() if 'include "../Action/'+filename+'"' in l)
        assert before in line;text=text.replace(line,line.replace(before,after))
    needle='                incbin "../Resources/17_ACTION/'+data_path.name+'"';assert text.count(needle)==1
    repl=needle+'\n                assert $ == #3800\n                disp #9800\n                include "../Action/Data/ProjectionSquares.asm"\n                ent'
    pending[path]=text.replace(needle,repl).encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionProjectionClipState' not in text
    block='\n                ; Исходный байт выбора продолжения после граничного отбора\n                module ActionProjectionClipState\n'
    block+='SkipDetail      equ #6F59'.ljust(80)+'; 00 допускает E299, полный ненулевой байт переводит E40F\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionProjectionClipConst' not in text
    block='\n                ; Исходные параметры таблицы двух граничных осей\n                module ActionProjectionClipConst\n'
    for label,value,note in (('SquarePage',0x98,'старший байт исходной страницы нормированных квадратов'),
        ('WidthBase',0x48,'перед SRA задаёт центр первой оси 36'),('HeightBase',0x42,'перед SRA задаёт центр второй оси 33')):
        block+=(label.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FSymmetricSquareValue' not in text
    block='\n                ; Физический байт исходной таблицы граничных поправок\n                struct FSymmetricSquareValue\n'
    block+='Value           db 0'.ljust(80)+'; нормированный квадрат min(i,255-i)^2 DIV 127\n                ends\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionProjectionClipFacts import FUNCTIONS as ACTION_PROJECTION_CLIP_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_PROJECTION_CLIP_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionProjectionClipFacts import CONTRACTS as ACTION_PROJECTION_CLIP_CONTRACTS\nCONTRACTS.update(ACTION_PROJECTION_CLIP_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_projection_clip_name_operands(region,function_address,operation)')
    text+="\nfrom ActionProjectionClipFacts import name_operands as action_projection_clip_name_operands\nDOCUMENTS['Action',0xE213]=('ActionProjectionClip','граничный отбор')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    text=text.replace(needle,"\nfrom ActionProjectionClipFacts import COMMENTS as ACTION_PROJECTION_CLIP_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTION_CLIP_COMMENTS)\n"+needle)
    needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические 256 нормированных квадратов исходной страницы 9800.
    if "struct FSymmetricSquareValue" in (ROOT/"Includes/Structs/Include.inc").read_text("utf-8"):
        from ActionProjectionClipFacts import TABLE as PROJECTION_SQUARES, render as render_projection_squares
        text,bindings=render_projection_squares(data_by_slot[17])
        write(PROJECTION_SQUARES[1],text)
        symbols.update(bindings)
        special[17,0x3800]=(0x3900,PROJECTION_SQUARES[1],0x9800)
'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8');needle='    # Проверка физических записей композиции и точной грамматики фактических DB-команд.';assert text.count(needle)==1
    hook='''    # Проверка всех исходных байтов нормированных квадратов и каждого физического поля.
    from ActionProjectionClipFacts import TABLE as PROJECTION_SQUARES, parse as parse_projection_squares
    projection_square_values=0
    entries=[i for i in source_map if i['path']==PROJECTION_SQUARES[1]]
    if entries:
        assert len(entries)==1
        item=entries[0]
        raw,labels=parse_projection_squares((ROOT/PROJECTION_SQUARES[1]).read_text('utf-8'))
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(17,0x3800,256,0x9800)
        assert raw==sources[17][0x3800:0x3900]
        assert list(raw)==[min(i,255-i)**2//127 for i in range(256)]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        assert symbols['FSYMMETRICSQUAREVALUE']==1 and symbols['FSYMMETRICSQUAREVALUE.VALUE']==0
        projection_square_values=256

'''
    text=text.replace(needle,hook+needle);needle="    report['type_delta_records'] = type_delta_records";assert text.count(needle)==1
    pending[path]=text.replace(needle,needle+"\n    report['projection_square_values'] = projection_square_values").encode('utf-8')
    for relative in ('Docs/DataFormats.md','Tools/Disasm/Research/GenerateDocs.py'):
        path=ROOT/relative;text=path.read_text('utf-8');needle='| FIndexedDelta | #01 |';index=text.index(needle);begin=text.rfind('\n',0,index)+1
        row='| FSymmetricSquareValue | #01 | 256 физических нормированных квадратов, см. [ActionProjectionClip](ActionProjectionClip.md) |'
        addition='               "'+row+'",\n' if relative.endswith('.py') else row+'\n'
        pending[path]=(text[:begin]+addition+text[begin:]).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text);needle='| #E299 | [Action.PrepareProjectedBounds]';assert text.count(needle)==1
    row='| #E213 | [Action.'+name+'](../'+new_path+') | '+description+' |\n';pending[path]=text.replace(needle,row+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## PrepareProjectedBounds\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+new_path+')\n\n'+description+'.\n\n[Граничные проверки, физическая таблица и модель](../ActionProjectionClip.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    for relative in ('Docs/ActionScaleHeader.md','Docs/ActionProjectedCapture.md','Docs/ActionProjectedBounds.md'):
        path=ROOT/relative;text=path.read_text('utf-8');text=text.replace('шесть частей (0)..(5)','семь частей (0)..(6)').replace('пять частей (0)..(4)','семь частей (0)..(6)')
        text+='\n[ClipProjectionBounds](ActionProjectionClip.md) теперь выделен по E213..E298 вместе с физической таблицей 9800. Неизвестными перед ним остаются 66 байтов E1D1..E212, весь окружающий обход по-прежнему не доказан.\n'
        pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionProjectionClip';history=ROOT/'Tools/Disasm/Research/History/BeforeActionProjectionClip'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Подготовка отдельного кандидата и проверка текущей рабочей копии перед публикацией.
    for current,before,after in plan:
        target=candidate/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current,before,after in plan:assert current.read_bytes()==before if before is not None else not current.exists()
    for current,before,after in plan:
        if before is not None:
            target=history/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for current,before,after in plan:current.parent.mkdir(parents=True,exist_ok=True);current.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,described_functions=1,proved_local_code_bytes=134,confirmed_instructions=len(records),
        physical_table_bytes=256,physical_table_records=256,physical_symbol_bindings=len(labels),
        remaining_unknown_code_bytes=66,original_bytes_preserved=True,model_cases=267008,whole_projection_scan_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectionClipClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
