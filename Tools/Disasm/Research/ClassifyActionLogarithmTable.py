"""Уточнение названия существующего построителя и его полного договора, исходные байты не меняются."""
import contextlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from SourcePresentation import format_function
from ValidateNotes import validate_notes
import ActionLogarithmTableFacts as facts


def main(facts=facts,tag='ActionLogarithmTable',address=0x438F,old_name_expected='BuildReciprocalTable',state_fields=None):
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read(tag+'Verification');assert proof['passed'] and proof['total_cases']==256
    functions,source_map,symbols,modified,flow=[read(n) for n in ('Functions','SourceMap','Symbols','ModifiedCode','ControlFlow')]
    function=next(f for f in functions if f['region']=='ActionBoot' and f['address']==address)
    old_name=function['name'];assert old_name==old_name_expected;old_path=ROOT/function['path']
    assert 'Unknown, регистровый контракт ещё не доказан' in old_path.read_text('utf-8')
    name,description=facts.FUNCTIONS[address];new_path='Source/ActionBoot/'+name+'.asm';old_description=function['description']
    end=address+function['end_offset']-function['offset']
    region=next(r for r in flow if r['name']=='ActionBoot');records=[i for i in region['instructions'] if address<=i['address']<end]
    validate_notes([region],{'ActionBoot':facts.COMMENTS})
    replacements={old_name:name,**{'Point'+format(a,'04X'):n for a,n in facts.LOCAL.items()}}
    def rename(text):
        for old,new in replacements.items():text=re.sub(r'\b'+old+r'\b',new,text)
        return text
    # Поиск только ссылок на переименуемый вход и его файл, без массового изменения других функций.
    pending={}
    for directory,patterns in (('Source',('*.asm','*.inc')),('Docs',('*.md',))):
        for pattern in patterns:
            for path in (ROOT/directory).rglob(pattern):
                text=path.read_text('utf-8')
                if old_name in text and path!=old_path:pending[path]=rename(text).encode('utf-8')
    labels={address:'Entry',**facts.LOCAL}
    lines=['                module ActionBoot','                module '+name,
        '                ; Документация [формула и проверка таблицы](../../Docs/'+tag+'.md)',
        '                ; -----------------------------------------','                ; '+description,
        '                ; исходная запись 17, загрузчик '+format(address,'04X')+'..'+format(end-1,'04X')]
    for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['ActionBoot',address]):
        lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
    lines.append('                ; -----------------------------------------')
    for record in records:
        pc=record['address'];before,right=facts.COMMENTS.get(pc,([],None));lines+=['                ; '+v for v in before]
        op=record['operation'].replace(',',', ')
        for target,label in labels.items():
            if op.startswith(('JR ','JP ','CALL ','DJNZ ')):op=op.replace('#'+format(target,'04X'),'@ActionBoot.'+name+'.'+label)
        op=facts.name_operands('ActionBoot',address,op);label=labels.get(pc,'')
        line=((label+':').ljust(16) if label else ' '*16)+op
        if right:assert len(line)<80;line=line.ljust(80)+'; '+right
        lines.append(line)
    lines+=['                endmodule','                endmodule'];pending[ROOT/new_path]=format_function('\n'.join(lines)+'\n').encode('utf-8')
    old_relative=function['path'];function.update(name=name,description=description,path=new_path,semantic_status='described')
    for item in source_map:
        if item['path']==old_relative:item['path']=new_path
    for item in modified:
        if item['path']==old_relative:item['path']=new_path
    symbols={rename(k):v for k,v in symbols.items()}
    for stem,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');assert 'module '+tag not in text
    block='\n                ; Исходные страницы генерируемой таблицы, память не выделяется\n                module '+tag+'\n'
    if state_fields is None:state_fields=(('LowPage',0x9100,'младшие байты T[0..255]'),('HighPage',0x9200,'старшие байты T[0..255]'))
    for label,value,note in state_fields:
        block+=(label.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    pending[path]=text.replace('                endif',block+'                endmodule\n\n                endif').encode('utf-8')
    prefix=re.sub(r'(?<!^)(?=[A-Z][a-z])','_',tag).upper();handler=prefix.lower()+'_name_operands'
    for filename,extra in (
        ('Knowledge.py',f"\nfrom {tag}Facts import FUNCTIONS as {prefix}_FUNCTIONS\nFUNCTIONS['ActionBoot'].update({prefix}_FUNCTIONS)\n"),
        ('Contracts.py',f"\nfrom {tag}Facts import CONTRACTS as {prefix}_CONTRACTS\nCONTRACTS.update({prefix}_CONTRACTS)\n")):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8');assert extra.strip().splitlines()[0] not in text;pending[path]=(text+extra).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = '+handler+'(region,function_address,operation)')
    text+=f"\nfrom {tag}Facts import name_operands as {handler}\nDOCUMENTS['ActionBoot',{address}]=('{tag}','формула таблицы')\n"
    text+='LABELS.update('+repr({('ActionBoot',a):n for a,n in facts.LOCAL.items()})+')\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    pending[path]=text.replace(needle,f"\nfrom {tag}Facts import COMMENTS as {prefix}_COMMENTS\nREGION_COMMENTS.setdefault('ActionBoot',{{}}).update({prefix}_COMMENTS)\n"+needle).encode('utf-8')
    for relative in ('Docs/Functions.md','Docs/FunctionDetails/ActionBoot.md'):
        path=ROOT/relative;text=pending[path].decode('utf-8');text=text.replace(old_description,description)
        if relative.endswith('ActionBoot.md'):
            start=text.index('## '+name+'\n');end=text.find('\n## ',start+4);end=len(text) if end<0 else end
            text=text[:end]+'\n[Формула, оба регистровых набора и независимая модель](../'+tag+'.md).\n'+text[end:]
        pending[path]=text.encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag);history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Сохранение отдельного кандидата и проверка рабочей копии перед публикацией.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for path,before,after in plan:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    # Удаление только переименованного исходника после проверки неизменности инструкций и истории.
    assert old_path.resolve().is_relative_to((ROOT/'Source/ActionBoot').resolve()) and old_path.read_bytes()==(history/old_relative).read_bytes();old_path.unlink()
    result=dict(passed=True,described_functions=1,previously_named_contract_proved=True,instructions_changed=0,
        physical_bytes_preserved=True,independent_model_cases=256,generated_table_bytes=proof['physical_table_bytes'],assembly_executed=False)
    (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
