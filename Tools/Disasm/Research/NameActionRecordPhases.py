"""Имена трёх реальных фазовых индексов записи и их физические экземпляры."""
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

FIELDS={7:('OffsetPhase0','байтовый индекс первой фазовой пары вычислителя смещения'),
        8:('OffsetPhase1','байтовый индекс второй фазовой пары, подготовитель добавляет 128'),
        9:('OffsetPhase2','байтовый индекс третьей фазовой пары вычислителя смещения')}


def main():
    assert all(len(name)<=15 for name,_ in FIELDS.values())
    with contextlib.redirect_stdout(io.StringIO()):verify()
    pending={}
    for path in (ROOT/'Source').rglob('*.asm'):
        text=path.read_text('utf-8');after=text
        affected=[]
        for offset,(name,_) in FIELDS.items():
            old=f'Unknown{offset:02X}'
            if 'FActionRecord.'+old in text:
                affected.append((old,name))
                after=after.replace('FActionRecord.'+old,'FActionRecord.'+name)
        for old,name in affected:
            after=after.replace(old,name)
        if after!=text:
            lines=[]
            for line in after.splitlines():
                code,sep,note=line.partition(';')
                if sep and any(name in code for name,_ in FIELDS.values()):
                    line=code.rstrip().ljust(80)+';'+note
                lines.append(line)
            pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    # Обновление только действующих фактов полей записи, одноимённые параметры 65E0..65E4 не затрагиваются.
    for filename in ('ActionMissileCreationFacts.py','ActionObjectOffsetFacts.py',
                     'ActionObjectOffsetTransferFacts.py','ActionRecordCodeStepFacts.py','ConfirmedIndexedFields.py'):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8')
        for offset,(name,_) in FIELDS.items():text=text.replace(f'Unknown{offset:02X}',name)
        pending[path]=text.encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    for offset,(name,note) in FIELDS.items():
        needle=f'Unknown{offset:02X}       db #00                                                          ; игровой смысл ещё неизвестен, 60AE обнуляет'
        assert text.count(needle)==1
        text=text.replace(needle,(name.ljust(16)+'db #00').ljust(80)+'; '+note)
    # Проверка принадлежности последнего байта шаблона именно полю записи 08 перед согласованием имени.
    assert text.count('RecordByte08    db #00')==1
    text=text.replace('RecordByte08    db #00','OffsetPhase1    db #00')
    text=text.replace('байт, записываемый в FActionRecord.Unknown08','байт, записываемый в FActionRecord.OffsetPhase1')
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionObjectRecords.py';text=path.read_text('utf-8')
    marker="       10:('StateCode'"
    assert text.count(marker)==1
    additions=''.join(f"       {offset}:('{name}','{note}'),\n" for offset,(name,note) in FIELDS.items())
    pending[path]=text.replace(marker,additions+marker).encode('utf-8')
    path=ROOT/'Source/Action/Data/ObjectRecords.asm';text=path.read_text('utf-8')
    for offset,(name,note) in FIELDS.items():
        needle=f'; Unknown{offset:02X}, игровой смысл ещё неизвестен, 60AE обнуляет'
        assert text.count(needle)==26
        text=text.replace(needle,'; '+name+', '+note)
    pending[path]=text.encode('utf-8')
    for filename in ('Source/Action/Data/SpawnTemplates.asm',
                     'Tools/Disasm/Research/SpawnPhysicalRows.py',
                     'Tools/Disasm/Research/PublishSpawnPhysicalRows.py'):
        path=ROOT/filename;text=pending.get(path,path.read_bytes()).decode('utf-8')
        text=text.replace('RecordByte08','OffsetPhase1').replace('FActionRecord.Unknown08','FActionRecord.OffsetPhase1')
        pending[path]=text.encode('utf-8')
    # Согласование двух экспортных таблиц с общей физической схемой вместо устаревшего построения Unknown06 и Unknown0A.
    for filename in ('ActionSpawnRecordFinishFacts.py','ActionSpawnScheduleFacts.py'):
        path=ROOT/'Tools/Disasm/Research'/filename;text=path.read_text('utf-8')
        if filename=='ActionSpawnRecordFinishFacts.py':
            needle="        fields[offset] = 'Unknown' + offset"
            replacement="        fields[offset] = KNOWN.get(int(offset, 16), ('Unknown' + offset,))[0]"
        else:
            needle="fields.update({offset: 'Unknown' + offset for offset in"
            replacement="fields.update({offset: KNOWN.get(int(offset, 16), ('Unknown' + offset,))[0] for offset in"
        assert text.count(needle)==1
        text=text.replace(needle,replacement)
        text+='\nfrom ActionObjectRecords import KNOWN\n'
        pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Reports/Symbols.json';symbols=json.loads(path.read_text('utf-8'))
    renamed=0
    for offset,(name,_) in FIELDS.items():
        count=0
        for key in tuple(symbols):
            if key.startswith('ActionObjectRecords.') and key.endswith(f'.Unknown{offset:02X}'):
                new=key.rsplit('.',1)[0]+'.'+name;assert new not in symbols
                symbols[new]=symbols.pop(key);count+=1
        assert count==26
        renamed+=count
    pending[path]=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    for path in (ROOT/'Docs').glob('Action*.md'):
        text=path.read_text('utf-8');after=text
        for offset,(name,_) in FIELDS.items():
            after=after.replace('FActionRecord.Unknown'+f'{offset:02X}','FActionRecord.'+name)
        if path.name in ('ActionRecordCodeStep.md','ActionObjectOffsetTransfer.md'):
            for offset,(name,_) in FIELDS.items():after=after.replace(f'Unknown{offset:02X}',name)
        if after!=text:pending[path]=after.encode('utf-8')
    path=ROOT/'Docs/ActionObjectRecords.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    marker='| 0A | StateCode |';assert text.count(marker)==1
    table=''.join(f'| {offset:02X} | {name} | {note[0].upper()+note[1:]} |\n' for offset,(name,note) in FIELDS.items())
    text=text.replace(marker,table+marker).replace('Unknown07 и другие неустановленные поля','Unknown0D и другие неустановленные поля')
    text+='''
## Фазовые индексы 07..09

OffsetPhase0, OffsetPhase1 и OffsetPhase2 задают три индекса исходной
256-байтовой синусоиды 9900. Единица поля соответствует одному индексу
страницы, арифметика оборачивается по модулю 256. Все разряды 7..0
образуют одно число, независимые флаги не назначаются. Нулевое значение
выбирает индекс ноль, на исходной странице его синус равен нулю.

[PrepareObjectOffsetTransform](../Source/Action/PrepareObjectOffsetTransform.asm)
передаёт первое и третье поля прямо, ко второму добавляет 128.
[BuildObjectOffsetCoefficients](../Source/Action/BuildObjectOffsetCoefficients.asm)
читает для каждого индекса пару значений с расстоянием 64 и вычисляет
три коэффициента. Имена пространственных осей не установлены и полям
не приписываются. [StepRecordTargetCodes](../Source/Action/StepRecordTargetCodes.asm)
подводит второе и третье поля к двум рассчитанным кодам по своим
различным правилам ограничения шага. [Физические шаблоны](ActionSpawnPhysicalRows.md)
содержат начальный OffsetPhase1. Разметка подтверждает использование
полей на разобранных путях, а не завершённость всех игровых классов.
'''
    pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ActionSpawnPhysicalRows.md';text=path.read_text('utf-8')
    pending[path]=text.replace('RecordByte08','OffsetPhase1').encode('utf-8')
    for filename in ('Source/Action/StepRecordTowardWideVector.asm',
                     'Tools/Disasm/Research/ActionWideTargetStepFacts.py',
                     'Docs/ActionWideTargetStep.md','Docs/ActionSpawnPhysicalRows.md'):
        path=ROOT/filename;text=pending.get(path,path.read_bytes()).decode('utf-8')
        text=text.replace('Unknown08/09','OffsetPhase1/OffsetPhase2')
        for offset,(name,_) in FIELDS.items():text=text.replace(f'Unknown{offset:02X}',name)
        pending[path]=text.encode('utf-8')
    for path in (*(ROOT/'Source').rglob('*.asm'), ROOT/'Tools/Disasm/Research/ConfirmedIndexedFields.py'):
        text=pending.get(path,path.read_bytes()).decode('utf-8')
        if 'FSpawnTemplateRow.RecordByte08' in text:
            pending[path]=text.replace('FSpawnTemplateRow.RecordByte08','FSpawnTemplateRow.OffsetPhase1').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRecordPhases'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionRecordPhases'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() for path in pending}
    for path,data in pending.items():
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Проверка основания каждого файла до публикации кандидата, ручные изменения не перезаписываются молча.
    for path,data in before.items():
        assert path.read_bytes()==data
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in pending.items():
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='record-phases-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(data)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(data)
    # Проверка уже записанных файлов в свежих схемах, прежний импорт не является проверкой нового состояния.
    for module in ('ActionObjectRecords','SpawnPhysicalRows'):
        if module in sys.modules:importlib.reload(sys.modules[module])
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    from ActionObjectRecords import layout
    size,fields=layout('FActionRecord');assert size==64
    assert all(fields[name]==offset for offset,(name,_) in FIELDS.items())
    for module in ('ActionSpawnRecordFinishFacts','ActionSpawnScheduleFacts'):
        if module in sys.modules:importlib.reload(sys.modules[module])
    from ActionSpawnRecordFinishFacts import name_operands as finish_operands
    from ActionSpawnScheduleFacts import name_operands as schedule_operands
    expected={6:'ModelOffset',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',10:'StateCode'}
    for offset,name in expected.items():
        for function,address,register in ((finish_operands,0x7DD4,'IX'),(schedule_operands,0x7859,'IY')):
            result=function('Action',address,f'LD ({register}+#{offset:02X}),A')
            assert 'FActionRecord.'+name in result
    report=dict(passed=True,record_size=size,field_offsets={name:offset for offset,(name,_) in FIELDS.items()},
                physical_record_field_symbols_renamed=renamed,files_changed=len(pending),
                spatial_axis_names_proved=False,source_instructions_and_physical_bytes_preserved=True,
                export_field_bindings_checked=10,
                assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordPhaseNaming.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
