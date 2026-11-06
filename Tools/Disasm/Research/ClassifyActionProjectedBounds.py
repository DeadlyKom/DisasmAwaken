"""Отделение доказанных 118 байтов подготовки проекции от неизвестного предшествующего обхода."""
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionProjectedBoundsFacts as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionProjectedBoundsVerification');assert proof['passed'] and proof['total_cases']==393417 and proof['paths']['y_overflow']>0
    functions,source_map,symbols,inventory,flow,modified=[read(n) for n in ('Functions','SourceMap','Symbols','Inventory','ControlFlow','ModifiedCode')]
    old=next(f for f in functions if f['region']=='Action' and f['address']==0xE1D1)
    assert (old['name'],old['end_offset'])==('UnknownE1D1',0x830F)
    current=ROOT/old['path'];old_text=current.read_text('utf-8');old_range=next(i for i in source_map if i['path']==old['path'])
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();pending={}
    name,description=facts.FUNCTIONS[0xE299];new_path='Source/Action/'+name+'.asm'
    first=dict(old,end_offset=0x8299)
    second=dict(old,name=name,address=0xE299,offset=0x8299,path=new_path,description=description,semantic_status='described')
    rename_symbols={}
    for key,value in symbols.items():
        if key.startswith('Action.UnknownE1D1.') and value>=0xE299:
            assert value in facts.LOCAL,(key,value)
            rename_symbols[key]='Action.'+name+'.'+facts.LOCAL[value]
    def rename(text):
        for before,after in rename_symbols.items():text=re.sub(r'\b'+re.escape(before)+r'\b',after,text)
        return text
    # Поиск только ссылок на перемещаемые внутренние метки, без переоформления соседних функций.
    for pattern in ('*.asm','*.inc'):
        for path in (ROOT/'Source').rglob(pattern):
            if path==current:continue
            text=path.read_text('utf-8');after=rename(text)
            if text!=after:pending[path]=after.encode('utf-8')
    region=next(r for r in flow if r['name']=='Action');records=[i for i in region['instructions'] if 0xE299<=i['address']<0xE30F]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==source[0x8299:0x830F]
    validate_notes([region],{'Action':facts.COMMENTS})
    lines=['                module Action','                module '+name,
        '                ; Документация [допуск и координаты](../../Docs/ActionProjectedBounds.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, код ACTION банка 0, адреса E299..E30E']
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Action',0xE299]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=record['operation'].replace(',',', ')
        for address,label in facts.LOCAL.items():op=op.replace('#'+format(address,'04X'),'@Action.'+name+'.'+label)
        op=op.replace('#E40F','@Action.UnknownE36A.PointE40F').replace('CALL #AE73','CALL @Action.DivideScaledLogarithmic.Entry')
        op=facts.name_operands('Action',0xE299,op);label='Entry' if pc==0xE299 else facts.LOCAL.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule']
    continuation=dict(region='Action',name='CaptureProjectedRecord',path='Source/Action/CaptureProjectedRecord.asm')
    pending[ROOT/new_path]=format_function('\n'.join(lines)+'\n',continuation).encode('utf-8')
    # Сохранение неизвестного префикса текстом текущей рабочей копии и обозначение нового последовательного продолжения.
    cut=old_text.index('                LD A, (#D9B7)\n');prefix=rename(old_text[:cut]).replace('E1D1..E30E','E1D1..E298')
    prefix+='                endmodule\n                endmodule\n'
    pending[current]=format_function(prefix,second).encode('utf-8')
    index=functions.index(old);functions[index:index+1]=[first,second]
    index=source_map.index(old_range);ranges=[]
    for f in (first,second):
        start,end=f['offset'],f['end_offset'];ranges.append(dict(old_range,offset=start,length=end-start,path=f['path'],origin=f['address'],sha256=hashlib.sha256(source[start:end]).hexdigest()))
    source_map[index:index+1]=ranges
    symbols={rename_symbols.get(k,k):v for k,v in symbols.items()};assert 'Action.'+name+'.Entry' not in symbols
    symbols['Action.'+name+'.Entry']=0xE299;region['roots']=sorted(set(region['roots'])|{0xE299})
    for item in modified:
        if item['path']==old['path'] and item['writer']>=0xE299:item['path']=new_path
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),unknown=sum(f['semantic_status']!='described' for f in functions))
    inventory['ranges_by_kind']['code']+=1
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=pending.get(path,path.read_bytes()).decode('utf-8')
    line=next(l for l in text.splitlines() if 'include "../Action/UnknownE1D1.asm"' in l)
    repl=line+'\n                ent\n                assert $ == #8299\n                disp #E299\n'
    repl+=('                include "../Action/'+name+'.asm"').ljust(80)+'; (3) жёсткий порядок продолжения E020'
    text=text.replace(line,repl)
    for filename,before,after in (('CaptureProjectedRecord.asm','(3)','(4)'),('UnknownE36A.asm','(4)','(5)')):
        line=next(l for l in text.splitlines() if 'include "../Action/'+filename+'"' in l)
        assert before in line;text=text.replace(line,line.replace(before,after))
    pending[path]=text.encode('utf-8')
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module ActionProjectedBoundsState' not in text
    block='\n                ; Существующие маска и операнды проекционного отбора, память не выделяется\n                module ActionProjectedBoundsState\n'
    for label,address,note in (('CompanionMask',0xE021,'полный байт маски, AND с Gate, игровой смысл ещё не установлен'),
        ('AbsoluteX',0xE372,'операнд LD BC,nn в E371, модуль отношения X'),('AbsoluteY',0xE375,'операнд LD DE,nn в E374, модуль отношения Y')):
        block+=(label.ljust(16)+'equ #'+format(address,'04X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    path=ROOT/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert 'module ActionProjectedBoundsConst' not in text
    block='\n                ; Подтверждённый предел модуля старшего байта координаты\n                module ActionProjectedBoundsConst\n'
    block+='HighByteLimit   equ #0A'.ljust(80)+'; модуль signed8 старшего байта должен быть меньше 10\n                endmodule\n\n'
    pending[path]=text.replace('                endif',block+'                endif').encode('utf-8')
    for filename,extra in (
        ('Knowledge.py',"\nfrom ActionProjectedBoundsFacts import FUNCTIONS as ACTION_PROJECTED_BOUNDS_FUNCTIONS\nFUNCTIONS['Action'].update(ACTION_PROJECTED_BOUNDS_FUNCTIONS)\n"),
        ('Contracts.py',"\nfrom ActionProjectedBoundsFacts import CONTRACTS as ACTION_PROJECTED_BOUNDS_CONTRACTS\nCONTRACTS.update(ACTION_PROJECTED_BOUNDS_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_projected_bounds_name_operands(region,function_address,operation)')
    text+="\nfrom ActionProjectedBoundsFacts import name_operands as action_projected_bounds_name_operands\nDOCUMENTS['Action',0xE299]=('ActionProjectedBounds','подготовка допуска и координат')\n"
    text+='LABELS.update('+repr({('Action',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,"\nfrom ActionProjectedBoundsFacts import COMMENTS as ACTION_PROJECTED_BOUNDS_COMMENTS\nREGION_COMMENTS.setdefault('Action',{}).update(ACTION_PROJECTED_BOUNDS_COMMENTS)\n"+needle).encode('utf-8')
    path=ROOT/'Docs/Functions.md';text=path.read_text('utf-8');total=sum(f['region']=='Action' for f in functions);described=sum(f['region']=='Action' and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| Action \| \d+ \| \d+ \|',f'| Action | {total} | {described} |',text)
    needle='| #E30F |';assert text.count(needle)==1
    row='| #E299 | [Action.'+name+'](../'+new_path+') | '+description+' |\n';pending[path]=text.replace(needle,row+needle).encode('utf-8')
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8');needle='## CaptureProjectedRecord\n';assert text.count(needle)==1
    section='## '+name+'\n\n[Action.'+name+'](../../'+new_path+')\n\n'+description+'.\n\n[Три отношения, ранние выходы и модели](../ActionProjectedBounds.md).\n\n'
    pending[path]=text.replace(needle,section+needle).encode('utf-8')
    for relative in ('Docs/ActionScaleHeader.md','Docs/ActionProjectedCapture.md'):
        path=ROOT/relative;text=path.read_text('utf-8');text=text.replace('пять частей (0)..(4)','шесть частей (0)..(5)').replace('пяти частей (0)..(4)','шести частей (0)..(5)')
        if relative.endswith('ActionProjectedCapture.md'):
            text+='\n[PrepareProjectedBounds](ActionProjectedBounds.md) выделен из E299..E30E, неизвестными до него остаются 200 байтов E1D1..E298. Ранее упомянутые 318 байтов относились к срезу до этого выделения.\n'
        else:text+='\nСледующие три отношения выделены в [PrepareProjectedBounds](ActionProjectedBounds.md), неизвестный префикс теперь ограничен E1D1..E298.\n'
        pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionProjectedBounds';history=ROOT/'Tools/Disasm/Research/History/BeforeActionProjectedBounds'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Создание отдельного кандидата и проверка текущей рабочей копии перед публикацией, staged-состояние сохраняется.
    for current,before,after in plan:
        target=candidate/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current,before,after in plan:assert current.read_bytes()==before if before is not None else not current.exists()
    for current,before,after in plan:
        if before is not None:
            target=history/current.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for current,before,after in plan:current.parent.mkdir(parents=True,exist_ok=True);current.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,described_functions=1,proved_local_code_bytes=118,confirmed_instructions=len(records),
        remaining_unknown_code_bytes=200,original_bytes_preserved=True,model_cases=393417,
        all_seven_paths_checked=True,partial_writes_preserved=True,whole_projection_scan_proved=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectedBoundsClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
