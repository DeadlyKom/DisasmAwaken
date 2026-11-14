"""Уточнение одного существующего байта по доказанным писателям и потребителям, без изменения структуры."""
from pathlib import Path
import contextlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))


def main():
    old='FF заставляет FindReusableRecord обнулить байт и однократно пропустить запись'
    new='FF задаёт однократный пропуск поиска, в отдельных состояниях биты 1..0 задают счётчик, бит 2 запрос детей, бит 4 допуск эффекта'
    pending={};counts={}
    for filename,count in (('Tools/Disasm/Research/ActionObjectRecords.py',1),('Includes/Structs/Include.inc',1),('Source/Action/Data/ObjectRecords.asm',26)):
        path=ROOT/filename;text=path.read_text('utf-8');assert text.count(old)==count
        pending[path]=text.replace(old,new).encode('utf-8');counts[filename]=count
    path=ROOT/'Docs/ActionObjectRecords.md';text=path.read_text('utf-8')
    text=text.replace('имеет 22 опубликованных обработчика','имеет 22 физических указателя на обработчики')
    assert '## Установленные контексты разрядов ReuseByte' not in text
    text+='''
## Установленные контексты разрядов ReuseByte

Физический байт по 18 совмещает полный код однократного пропуска и
поля отдельных алгоритмов. Он не переименован в восемь независимых
флагов. Для контекстов опубликованных ниже процедур схема разрядов:

```text
разряд       7 6 5 4 3 2 1 0
назначение   ? ? ? E ? S N N
```

`NN`, маска 03, число оставшихся попыток создания класса 19 по
[CreateCargoAndUpdateList](ActionClass19Spawn.md). Ноль запрещает попытку,
1..3 уменьшаются до поиска места с сохранением остальных шести битов.
Это одно двухбитовое число. Отказ поиска не восстанавливает попытку.

`S`, бит 2, маска 04, [SpawnLinkedClass9Records](ActionChildSpawn.md)
проверяет его как уже инициированный запрос. Ноль допускает случайную
проверку, единица возвращает управление без обновления потока. Бит
устанавливается после случайного допуска, до поиска места и остаётся
установленным при отказе выделения. Его явно сбрасывает
[HandleSelectedRecordProximity](ActionSelectedRecordProximity.md) у
выбранной ближней записи до освобождения текущей.

`E`, бит 4, маска 10, создатель класса 19 устанавливает его при
нормализованном коде x<5, иначе обнуляет весь ReuseByte ребёнка.
[State0E](ActionLinkedProximity.md) использует исходный бит 4 выбранной
ближней записи для допуска большого эффекта, затем весь байт уже
заменён FF пометкой освобождения. Другой установленный потребитель
[CheckCloseRecordComponents](ActionCloseRecord.md) также проверяет
этот разряд в собственном контексте. Общее игровое имя флага не назначено.

Знаки `?` означают, что общий смысл разрядов 7, 6, 5 и 3 этой разметкой
не установлен. Заполнение нулями само по себе не доказывает их отсутствия.
Полный FF продолжает означать однократный пропуск для
[FindReusableRecord](ActionRecordSearch.md), когда первая компонента
записи допускает просмотр как свободной. Поиск обнуляет байт и пропускает
его в этом проходе. Нельзя трактовать FF только как одновременную установку
всех независимых признаков. Полный ноль означает нулевой счётчик и
сброшенные опубликованные разряды, доступность самой записи определяется
отдельно по Component0 и маркеру.

Физические 26 экземпляров, структура FActionRecord, все размеры,
смещения и исходные 1664 байта сохранены. Уточнены только комментарии.
'''
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionReuseByteContexts'
    history=ROOT/'Tools/Disasm/Research/History/BeforeActionReuseByteContexts'
    assert not candidate.exists() and not history.exists();plan=[(path,path.read_bytes(),after) for path,after in pending.items()]
    # Подготовка отдельного кандидата и сверка оснований, никакие поля и значения инициализаторов не заменяются.
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        path.write_bytes(after)
    from VerifySources import main as verify
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,physical_instances_annotated=26,structure_bytes_unchanged=64,
        raw_initial_record_bytes_preserved=1664,shared_rules_duplicated_in_project=False,
        comment_replacements=counts,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionReuseByteContextsClassification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
