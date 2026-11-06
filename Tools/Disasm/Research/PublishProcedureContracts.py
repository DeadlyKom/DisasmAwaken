"""Публикация контрактов уже описанных процедур, без повторного массового экспорта."""
from pathlib import Path
import contextlib
import io
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def publish(tag,facts,document):
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=json.loads((ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')).read_text('utf-8'))
    assert proof['passed']
    functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'))
    chosen=[f for f in functions if (f['region'],f['address']) in facts.CONTRACTS]
    assert len(chosen)==len(facts.CONTRACTS) and all(f['semantic_status']=='described' for f in chosen)
    pending={}

    def update(relative,text):
        path=ROOT/relative
        pending[relative]=(path.read_bytes(),text.encode('utf-8'))

    symbols=json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_text('utf-8'))
    renames={}
    for (region,address),label in getattr(facts,'LABELS',{}).items():
        assert len(label)<=15
        previous=[s for s,a in symbols.items() if a==address and s.startswith(region+'.')]
        assert len(previous)==1,(region,address,previous)
        before=previous[0];after=before.rsplit('.',1)[0]+'.'+label
        assert after not in symbols
        symbols[after]=symbols.pop(before);renames[before]=after
    if renames:update('Tools/Disasm/Reports/Symbols.json',json.dumps(symbols,ensure_ascii=False,indent=2)+'\n')
    # Обновление только выбранных заголовков, доказанных операндов и зависимых целей переходов.
    chosen_by_path={f['path']:f for f in chosen}
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8')) if getattr(facts,'COMMENTS',{}) else []
    if flow:
        from ValidateNotes import validate_notes
        validate_notes(flow,{region:facts.COMMENTS for region in {f['region'] for f in chosen}})
    for path in (ROOT/'Source').rglob('*.asm'):
        relative=path.relative_to(ROOT).as_posix();before=path.read_text('utf-8');text=before
        for old,new in renames.items():text=text.replace('@'+old,'@'+new)
        if relative in chosen_by_path:
            f=chosen_by_path[relative];contract=facts.CONTRACTS[f['region'],f['address']]
            start=text.index('; In:');end=text.index('; -----------------------------------------',start)
            if ';   Unknown, регистровый контракт ещё не доказан' not in text:
                previous=getattr(facts,'EXPECTED_CONTRACTS',{}).get((f['region'],f['address']))
                assert previous is not None,relative
                expected_header=[]
                for heading,values in zip(('In','Out','Corrupt','Note'),previous):
                    expected_header+=['; '+heading+':']+[';   '+v for v in values]
                assert [v.strip() for v in text[start:end].splitlines() if v.strip()]==expected_header,relative
            header=[]
            for heading,values in zip(('In','Out','Corrupt','Note'),contract):
                header+=['                ; '+heading+':']+['                ;   '+v for v in values]
            text=text[:start]+'\n'.join(header)+'\n                '+text[end:]
            text=text.replace('; Документация ['+f['region']+'](../../Docs/FunctionDetails/'+f['region']+'.md)',
                '; Документация ['+f['region']+'](../../Docs/FunctionDetails/'+f['region']+'.md)\n                ; Документация [алгоритм и проверка](../../Docs/'+document+'.md)')
            for old,new in renames.items():
                if old.startswith(f['region']+'.'+f['name']+'.'):
                    text=re.sub(r'^'+old.rsplit('.',1)[1]+r':\s*',
                        (new.rsplit('.',1)[1]+':').ljust(16),text,flags=re.M)
            decoded=[i for r in flow if r['name']==f['region'] for i in r['instructions']
                if i['slot']==f['slot'] and f['offset']<=i['offset']<f['end_offset']]
            instruction_index=0;lines=[]
            for line in text.splitlines():
                if line.strip() and not line.lstrip().startswith(';'):
                    code,sep,note=line.partition(';')
                    operation=code[16:].strip()
                    if decoded and not operation.lower().startswith(('module ','endmodule')):
                        pc=decoded[instruction_index]['address'];instruction_index+=1
                        before_notes,right=getattr(facts,'COMMENTS',{}).get(pc,([],None))
                        lines+=['                ; '+v for v in before_notes]
                        if right:sep,note=';',' '+right
                    if hasattr(facts,'name_operands'):
                        code=code[:16]+facts.name_operands(f['region'],f['address'],code[16:])
                    line=code.rstrip().ljust(80)+';'+note if sep else code
                lines.append(line)
            assert not decoded or instruction_index==len(decoded)
            text='\n'.join(lines)+'\n'
        elif text!=before:
            text='\n'.join(code.rstrip().ljust(80)+';'+note if sep and code.strip() else line
                for line in text.splitlines() for code,sep,note in (line.partition(';'),))+'\n'
        if text!=before:update(relative,text)
    prefix=re.sub(r'(?<!^)(?=[A-Z][a-z])','_',tag).upper()
    hook=prefix.lower()+'_name_operands'
    relative='Tools/Disasm/Research/Contracts.py';text=(ROOT/relative).read_text('utf-8')
    assert 'from '+tag+'Facts import' not in text
    update(relative,text+'\nfrom '+tag+'Facts import CONTRACTS as '+prefix+'_CONTRACTS\nCONTRACTS.update('+prefix+'_CONTRACTS)\n')
    relative='Tools/Disasm/Research/SemanticNames.py';text=(ROOT/relative).read_text('utf-8')
    extra='\n'
    if hasattr(facts,'name_operands'):
        anchor='def name_operands(region, function_address, operation):'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n    operation = '+hook+'(region, function_address, operation)')
        extra+='from '+tag+'Facts import name_operands as '+hook+'\n'
    if getattr(facts,'LABELS',{}):
        extra+='from '+tag+'Facts import LABELS as '+prefix+'_LABELS\nLABELS.update('+prefix+'_LABELS)\n'
    for f in chosen:extra+='DOCUMENTS['+repr(f['region'])+', '+str(f['address'])+'] = ('+repr(document)+', "алгоритм и проверка")\n'
    update(relative,text+extra)
    if getattr(facts,'COMMENTS',{}):
        relative='Tools/Disasm/Research/ExportSources.py';text=(ROOT/relative).read_text('utf-8')
        hook='\nfrom '+tag+'Facts import COMMENTS as '+prefix+'_COMMENTS\n'
        for region in {f['region'] for f in chosen}:
            hook+='REGION_COMMENTS.setdefault('+repr(region)+', {}).update('+prefix+'_COMMENTS)\n'
        anchor='\n\nif __name__ == "__main__":'
        assert text.count(anchor)==1
        update(relative,text.replace(anchor,'\n'+hook+anchor))
    for region in {f['region'] for f in chosen}:
        relative='Docs/FunctionDetails/'+region+'.md';text=(ROOT/relative).read_text('utf-8')
        for f in chosen:
            if f['region']!=region:continue
            anchor='['+region+'.'+f['name']+'](../../'+f['path']+')'
            assert text.count(anchor)==1
            text=text.replace(anchor,anchor+'\n\n[Алгоритм, контракт и проверка](../'+document+'.md).')
        update(relative,text)
    for relative,marker,block in getattr(facts,'INCLUDE_BLOCKS',()):
        text=(ROOT/relative).read_text('utf-8');assert marker not in text
        assert text.count('                endif')==1
        update(relative,text.replace('                endif',block+'\n                endif'))
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag)
    history=ROOT/('Tools/Disasm/Research/History/Before'+tag)
    assert not candidate.exists() and not history.exists()
    # Сохранение раздельного кандидата и исходных контрольных копий.
    for relative,(before,after) in pending.items():
        for folder,data in ((candidate,after),(history,before)):
            path=folder/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    # Проверка отсутствия посторонних правок после подготовки кандидата.
    for relative,(before,_) in pending.items():assert (ROOT/relative).read_bytes()==before,relative
    for relative,(_,after) in pending.items():(ROOT/relative).write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    report=dict(passed=True,changed_files=list(pending),procedures=len(chosen),
        original_instructions_and_bytes_preserved=True,model_cases=proof['total_cases'],assembly_executed=False)
    (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
