"""Доказанные код восстановления, таймер фазового хода и числовой шаг целевых кодов."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify

FIELDS={0x16:('SavedStateCode','код состояния для восстановления в обработчиках хода и ожидания'),
        0x17:('PhaseMoveTimer','байтовый таймер вызовов обработчиков хода первой фазы'),
        0x25:('TargetCodeStep','числовой предельный шаг подвода второго и третьего фазовых кодов')}


def main():
    assert all(len(name)<=15 for name,_ in FIELDS.values())
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports'
    proofs=('ActionClass9LinkVerification','ActionObjectOffsetRiseVerification',
            'ActionObjectOffsetFallVerification','ActionObjectPhaseWaitVerification','ActionRecordCodeStepVerification')
    for name in proofs:assert json.loads((reports/(name+'.json')).read_text('utf-8'))['passed']
    pending={}
    for path in (ROOT/'Source/Action').glob('*.asm'):
        text=path.read_text('utf-8');after=text
        for offset,(name,_) in FIELDS.items():after=after.replace(f'Unknown{offset:02X}',name)
        if after!=text:
            lines=[]
            for line in after.splitlines():
                code,sep,note=line.partition(';')
                if sep and any(name in code for name,_ in FIELDS.values()):line=code.rstrip().ljust(80)+';'+note
                lines.append(line)
            pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    for path in (ROOT/'Tools/Disasm/Research').glob('*Facts.py'):
        text=path.read_text('utf-8');after=text
        if 'FActionRecord' not in text:continue
        for offset,(name,_) in FIELDS.items():after=after.replace(f'Unknown{offset:02X}',name)
        if after!=text:pending[path]=after.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ConfirmedIndexedFields.py';text=path.read_text('utf-8')
    for offset,(name,_) in FIELDS.items():text=text.replace(f'FActionRecord.Unknown{offset:02X}','FActionRecord.'+name)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8')
    for offset,(name,note) in FIELDS.items():
        old_note='игровой смысл ещё неизвестен'+(', 60AE записывает 02' if offset==0x25 else '')
        needle=(f'Unknown{offset:02X}'.ljust(16)+'db #00').ljust(80)+'; '+old_note
        assert text.count(needle)==1
        text=text.replace(needle,(name.ljust(16)+'db #00').ljust(80)+'; '+note)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ActionObjectRecords.py';text=path.read_text('utf-8')
    assert text.count('KNOWN={')==1
    additions=''.join(f"{offset}:('{name}','{note}'),\n       " for offset,(name,note) in FIELDS.items())
    pending[path]=text.replace('KNOWN={','KNOWN={'+additions).encode('utf-8')
    path=ROOT/'Source/Action/Data/ObjectRecords.asm';text=path.read_text('utf-8')
    for offset,(name,note) in FIELDS.items():
        needle=f'; Unknown{offset:02X}, игровой смысл ещё неизвестен'+(', 60AE записывает 02' if offset==0x25 else '')
        assert text.count(needle)==26
        text=text.replace(needle,'; '+name+', '+note)
    pending[path]=text.encode('utf-8')
    path=reports/'Symbols.json';symbols=json.loads(path.read_text('utf-8'));renamed=0
    for offset,(name,_) in FIELDS.items():
        count=0
        for key in tuple(symbols):
            if key.startswith('ActionObjectRecords.') and key.endswith(f'.Unknown{offset:02X}'):
                new=key.rsplit('.',1)[0]+'.'+name;assert new not in symbols
                symbols[new]=symbols.pop(key);count+=1
        assert count==26;renamed+=count
    pending[path]=(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    for path in (ROOT/'Docs').glob('Action*.md'):
        text=path.read_text('utf-8');after=text
        for offset,(name,_) in FIELDS.items():after=after.replace(f'Unknown{offset:02X}',name)
        if after!=text:pending[path]=after.encode('utf-8')
    path=ROOT/'Docs/ActionObjectRecords.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    marker='| 18 | ReuseByte |';assert text.count(marker)==1
    additions=''.join(f'| {offset:02X} | {name} | {note[0].upper()+note[1:]} |\n' for offset,(name,note) in FIELDS.items() if offset!=0x25)
    text=text.replace(marker,additions+marker)
    marker='| Прочие |';assert text.count(marker)==1
    text=text.replace(marker,'| 25 | TargetCodeStep | Числовой шаг подвода фазовых кодов, не набор флагов |\n'+marker)
    text+='''
## Восстанавливаемое состояние и числовые счётчики

SavedStateCode по 16 хранит код состояния, возвращаемый в StateCode
после хода либо ожидания. Его прямо читают
[AdvanceObjectOffsetFall](../Source/Action/AdvanceObjectOffsetFall.asm) и
[AdvanceObjectPhaseWait](../Source/Action/AdvanceObjectPhaseWait.asm).
[ConfigureClass9Link](../Source/Action/ConfigureClass9Link.asm) отдельно
распознаёт полный код 0D. Это один числовой код, а не независимые флаги,
нулевое значение при прямом восстановлении выбирает State00.
Полный игровой смысл всех кодов и всех классов этим не устанавливается.

PhaseMoveTimer по 17 уменьшается при каждом вызове двух обработчиков
хода. Смена состояния происходит при исходном таймере 1. Исходный ноль
не означает немедленное завершение, он оборачивается в FF. При переходе
из нарастания в спад записывается 1E, то есть 30 вызовов обработчика.
Единица здесь является вызовом соответствующего обработчика, перевод
в миллисекунды либо фиксированную частоту игровых кадров не утверждается.
Все восемь разрядов составляют числовой таймер.

TargetCodeStep по 25 задаёт предельный байтовый шаг
[StepRecordTargetCodes](../Source/Action/StepRecordTargetCodes.asm).
Два поля используют разные условия уменьшения шага и пропуска записи,
[точный алгоритм](ActionRecordCodeStep.md) сохраняет эти различия.
Нулевой шаг может приводить к записи прежнего значения, а не к пропуску
обработчика. Все разряды 7..0 относятся к числу. Создание ракеты пишет
02, подготовитель обычной записи выбирает 01 либо 02 по заголовку модели.
Адреса, физический размер записи и значения инициализации не изменены.
'''
    pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ActionRecordCodeStep.md';text=pending.get(path,path.read_bytes()).decode('utf-8')
    text=text.replace('Глобальные игровые оси и роли полей\nне назначаются по этому единственному потребителю, неизвестные имена\nв общей структуре сохранены.',
                      'Фазовое использование полей и числовой шаг установлены,\nглобальные игровые оси и все роли отдельных классов не назначаются\nпо одному потребителю. [Физическая структура](ActionObjectRecords.md).')
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRecordTimingFields'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionRecordTimingFields'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() for path in pending}
    for path,data in pending.items():
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Проверка каждого исходного файла перед заменой, пользовательский индекс остаётся нетронутым.
    for path,data in before.items():
        assert path.read_bytes()==data
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in pending.items():
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='record-timing-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(data)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(data)
    if 'ActionObjectRecords' in sys.modules:importlib.reload(sys.modules['ActionObjectRecords'])
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    from ActionObjectRecords import layout
    size,fields=layout('FActionRecord');assert size==64
    assert all(fields[name]==offset for offset,(name,_) in FIELDS.items())
    result=dict(passed=True,record_size=size,field_offsets={name:offset for offset,(name,_) in FIELDS.items()},
                physical_record_symbols_renamed=renamed,files_changed=len(pending),
                prior_original_instruction_models=proofs,source_bytes_and_instruction_sequence_preserved=True,
                timer_zero_wrap_preserved=True,zero_step_write_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ActionRecordTimingFieldNaming.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
