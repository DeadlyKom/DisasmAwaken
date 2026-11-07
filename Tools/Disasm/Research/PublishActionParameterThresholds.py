"""Три подтверждённых изменяемых порога и их писатели, без изменения дисковых инструкций."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify

FIELDS=(('Unknown07','Class0RLimit',0x6615,0xAC84,0x70,'поле 07, изменяемый операнд CP аппаратного R в ConfigureClass0Link'),
        ('Unknown08','RandomLowLimit',0xE6E7,0xAC89,0xA0,'поле 08, изменяемый операнд CP младшего байта Stream10 в FindFilteredRecordOr26'),
        ('Unknown0A','Class3RLimit',0x65E5,0xAC93,0x06,'поле 0A, изменяемый операнд CP аппаратного R в ConfigureClass3Link'))


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports'
    read=lambda name:json.loads((reports/(name+'.json')).read_text('utf-8'))
    assert read('ActionParameterThresholdsVerification')['passed']
    functions,flow,source_map,modified,symbols=(read(name) for name in ('Functions','ControlFlow','SourceMap','ModifiedCode','Symbols'))
    region=next(value for value in flow if value['name']=='Action');pending={}
    for old,new,target,writer,initial,note in FIELDS:
        assert len(new)<=15
        instruction=next(value for value in region['instructions'] if value['address']==target-1)
        source_writer=next(value for value in region['instructions'] if value['address']==writer)
        assert instruction['operation']==f'CP #{initial:02X}' and source_writer['operation']==f'LD (#{target:04X}),A'
        assert not any(value['region']=='Action' and value['writer']==writer for value in modified)
        owner=next(value for value in functions if value['region']=='Action' and value['address']<=target-1<value['address']+value['end_offset']-value['offset'])
        target_offset=instruction['offset']+1
        physical=next(value for value in source_map if value['slot']==17 and value['offset']<=target_offset<value['offset']+value['length'])
        assert physical['kind']=='code' and physical['path']==owner['path']
        modified.append(dict(region='Action',writer=writer,target=target,target_instruction=target-1,size=1,
            target_operation=instruction['operation'],path='Source/Action/ApplyParameterSet.asm',
            writer_bank=2,writer_offset=writer-0x6000,writer_source_classified=True,
            target_bank=5 if target<0x8000 else 0,target_region='Action',target_slot=17,
            target_offset=target_offset,target_source_classified=True,target_path=owner['path']))
        for key in tuple(symbols):
            if key.upper()==('ActionApplyParametersState.'+old).upper():
                renamed=key.rsplit('.',1)[0]+'.'+new;assert renamed not in symbols
                symbols[renamed]=symbols.pop(key)
    modified.sort(key=lambda value:(value['region'],value['writer'],value['target']))
    path=ROOT/'Includes/Variables/Include.inc';text=path.read_text('utf-8');inside=False;seen=set();lines=[]
    for line in text.splitlines():
        if line.strip()=='module ActionApplyParametersState':inside=True
        if inside:
            for old,new,target,_,_,note in FIELDS:
                if line.startswith(old.ljust(16)+'equ '):
                    assert f'#{target:04X}' in line
                    line=(new.ljust(16)+f'equ #{target:04X}').ljust(80)+'; '+note;seen.add(old)
        if line.strip()=='endmodule':inside=False
        lines.append(line)
    assert len(seen)==3
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    unknown_note='пять целей Unknown04, Unknown07, Unknown08, Unknown09 и Unknown0A пока не отнесены к доказанным инструкциям или полям данных'
    for filename in ('Source/Action/ApplyParameterSet.asm','Tools/Disasm/Research/ActionApplyParametersFacts.py'):
        path=ROOT/filename;text=path.read_text('utf-8');assert unknown_note in text
        text=text.replace(unknown_note,'две цели Unknown04 и Unknown09 пока не отнесены к доказанным инструкциям или полям данных')
        text=text.replace('десять остальных целей','тринадцать остальных целей')
        for old,new,_,_,_,_ in FIELDS:text=text.replace(old,new)
        text=text.replace('обновление Class0RLimit, назначение целевого потребителя не объявляется доказанным',
                          'обновление операнда Class0RLimit, порога аппаратного R для класса 0')
        text=text.replace('обновление RandomLowLimit в выбранном верхнем банке 0',
                          'обновление операнда RandomLowLimit, порога младшего байта Stream10 в банке 0')
        text=text.replace('обновление Class3RLimit, назначение целевого потребителя не объявляется доказанным',
                          'обновление операнда Class3RLimit, порога аппаратного R для класса 3')
        if filename.endswith('Facts.py'):
            for old,new,target,_,_,note in FIELDS:
                pattern=r"\('"+new+r"',0x"+f'{target:04X}'+r",'[^']*'\)"
                text,count=re.subn(pattern,f"('{new}',0x{target:04X},'{note}')",text)
                assert count==1
        else:
            text=text.replace('                module ApplyParameterSet',
                '                module ApplyParameterSet\n                ; Изменяемые пороги [писатели и влияние](../../Docs/ActionParameterThresholds.md)',1)
        pending[path]=text.encode('utf-8')
    changes=(
        ('Source/Action/ConfigureClass0Link.asm','ActionClass0LinkFacts.py','ConfigureClass0Link',
         (('R меньше 70','R меньше текущего Class0RLimit'),('F от CP 70','F от CP с Class0RLimit'),
          ('Проверка порога аппаратного R, распределение значений здесь не предполагается.',
           'Проверка текущего Class0RLimit, исходный порог 70 может быть изменён ApplyParameterSet.'))),
        ('Source/Action/FindFilteredRecordOr26.asm','ActionRandomFilteredRecordFacts.py','FindFilteredRecordOr26',
         (('не меньше A0','не меньше текущего RandomLowLimit'),('нового L с A0','нового L с текущим RandomLowLimit'))),
        ('Source/Action/ConfigureClass3Link.asm','ActionAdditionalClassFacts.py','ConfigureClass3Link',
         (('R>=06','R>=Class3RLimit'),('R<06','R<Class3RLimit'),
          ('R не меньше 06','R не меньше текущего Class3RLimit'),
          ('R меньше 06','R меньше текущего Class3RLimit'))))
    for source,facts,module,replacements in changes:
        for filename in (source,'Tools/Disasm/Research/'+facts):
            path=ROOT/filename;text=path.read_text('utf-8')
            for before,after in replacements:text=text.replace(before,after)
            if filename==source:
                text=text.replace('                module '+module,
                    '                module '+module+'\n                ; Изменяемый порог [параметры и проверка](../../Docs/ActionParameterThresholds.md)',1)
            pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ActionApplyParameters.md';text=path.read_text('utf-8')
    for old,new,target,_,_,note in FIELDS:
        lines=text.splitlines();matches=[index for index,line in enumerate(lines) if f'| {target:04X} | {old},' in line]
        assert len(matches)==1
        line=lines[matches[0]];lines[matches[0]]=line.split(f'| {target:04X} |')[0]+f'| {target:04X} | {new}, '+note.split(', ',1)[1]+' |'
        text='\n'.join(lines)+'\n'
    text+='\n[Три изменяемых порога](ActionParameterThresholds.md) связаны с реальными операндами CP и проверены для всех значений порога и сравниваемого байта. Это локальная роль трёх полей, полная игровая роль всех параметров ещё не установлена.\n'
    pending[path]=text.encode('utf-8')
    for filename,replacements in (
        ('Docs/ActionClass0Link.md',(('R<70','R<Class0RLimit'),('R>=70','R>=Class0RLimit'),('R меньше 70','R меньше Class0RLimit'))),
        ('Docs/ActionRandomFilteredRecord.md',(('не меньше A0','не меньше RandomLowLimit'),('меньше A0','меньше RandomLowLimit'),('L с A0','L с RandomLowLimit'))),
        ('Docs/ActionClass3Link.md',(('R не меньше 06','R не меньше Class3RLimit'),)),
        ('Docs/ActionAdditionalClassHandlers.md',(('R>=06','R>=Class3RLimit'),('R<06','R<Class3RLimit')))):
        path=ROOT/filename;text=path.read_text('utf-8')
        for before,after in replacements:text=text.replace(before,after)
        text+='\nТекущие операнды порогов могут изменяться ApplyParameterSet. Значения 70, A0 и 06 относятся к исходным байтам, а не ко всем игровым настройкам. [Писатели, точные переменные условия и проверка](ActionParameterThresholds.md).\n'
        pending[path]=text.encode('utf-8')
    for name,value in (('ModifiedCode',modified),('Symbols',symbols)):
        pending[reports/(name+'.json')]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionParameterThresholds'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionParameterThresholds'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() for path in pending}
    for path,data in pending.items():
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Проверка основания каждого файла перед публикацией, адреса и физические байты кода не меняются.
    for path,data in before.items():
        assert path.read_bytes()==data
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in pending.items():
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='parameter-thresholds-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(data)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    facts=importlib.import_module('ActionApplyParametersFacts');importlib.reload(facts)
    verified=read('ModifiedCode');facts.qualify_mutations(verified,flow,functions)
    result=dict(passed=True,code_operands_named=3,new_registered_writers=3,
        qualified_apply_targets=13,remaining_unknown_apply_targets=['Unknown04','Unknown09'],
        threshold_model_cases=196608,source_instructions_and_disk_bytes_preserved=True,
        assembly_executed=False,native_execution=False)
    (reports/'ActionParameterThresholdsClassification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
