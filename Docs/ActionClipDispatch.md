# Диспетчер отсечения ACTION C941

[ClipSingleEdge](../Source/Action/ClipSingleEdge.asm) задаёт режим одиночного ребра по CF03, очищает размер вывода 9BA3 и передаёт управление выбранному обработчику. Это документ первоначальной проверки границы. Полный вход и его регистровый договор теперь описаны в [ClipSingleEdge](ActionSingleEdge.md), все табличные пути в [ActionClipCases](ActionClipCases.md).

Если код первой точки равен F0, обе пятибайтовые точки CF0B и CF1B меняются местами. Иначе исходный порядок сохраняется. Индекс таблицы равен ((NOT First.ClipCode) AND F0) OR (Second.ClipCode AND 0F). Младший байт адреса читается из CF00+index, старший из D000+index. После INC H от CF до D0 основной F равен 90, он не сохраняет флаги предыдущего OR.

Перед JP (HL) три раза помещается адрес C993. Поэтому обработчик получает три подставных возврата над настоящим внешним адресом. Общий хвост C993 читает размер вывода, снимает два оставшихся подставных слова через POP DE и возвращается с флагами CP размера,4. Другая цепочка ClipPolygon использует собственный протокол возврата C071, эти рамки нельзя смешивать.

[Проверка границы диспетчеризации](../Tools/Disasm/Research/CheckActionClipDispatch.py) прошла 65792 сценария, все 65536 пары байтов кодов до косвенного перехода и 256 значений размера на общем хвосте. Проверяются точные регистры кроме R, все физические байты RAM и кратность записей. Табличные обработчики этой проверкой не исполняются. Проверка границы не является доказательством полного отсечения.

Девять нормальных кодов точек дают 81 допустимую пару. [Реестр таблицы](../Tools/Disasm/Reports/ActionClipDispatchTable.json) связывает каждую пару с существующим исходником. Рабочие байты CF03, CF07 и обеих точек лежат на недопустимых индексах таблицы, их записи не меняют адреса этих 81 пар. Все прочие возможные писатели и игровые профили этим утверждением не исчерпываются.

## Исходные цели для допустимых кодов

Таблица ниже показывает непосредственное чтение до возможного обмена точек F0. В реальном вызове после обмена индекс пересчитывается по новому порядку.

| Первый код | Второй код | Индекс | Адрес | Зарегистрированный вход |
| --- | --- | --- | --- | --- |
| F0 | F0 | 00 | C6D3 | [AppendSecondClipPoint](../Source/Action/AppendSecondClipPoint.asm) |
| F0 | E1 | 01 | C5E4 | [ClipInsideToRight](../Source/Action/ClipInsideToRight.asm) |
| F0 | D2 | 02 | C588 | [ClipInsideToLeft](../Source/Action/ClipInsideToLeft.asm) |
| F0 | B4 | 04 | C53D | [ClipInsideToBottom](../Source/Action/ClipInsideToBottom.asm) |
| F0 | 78 | 08 | C4F3 | [ClipInsideToTop](../Source/Action/ClipInsideToTop.asm) |
| F0 | A5 | 05 | C07B | [ClipInsideToBottomRight](../Source/Action/ClipInsideToBottomRight.asm) |
| F0 | 69 | 09 | C0AF | [ClipInsideToTopRight](../Source/Action/ClipInsideToTopRight.asm) |
| F0 | 96 | 06 | C095 | [ClipInsideToBottomLeft](../Source/Action/ClipInsideToBottomLeft.asm) |
| F0 | 5A | 0A | C0C9 | [ClipInsideToTopLeft](../Source/Action/ClipInsideToTopLeft.asm) |
| E1 | F0 | 10 | C0E3 | [ClipRightToInside](../Source/Action/ClipRightToInside.asm) |
| E1 | E1 | 11 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| E1 | D2 | 12 | C0E9 | [ClipRightToLeft](../Source/Action/ClipRightToLeft.asm) |
| E1 | B4 | 14 | C0EF | [ClipRightToBottom](../Source/Action/ClipRightToBottom.asm) |
| E1 | 78 | 18 | C119 | [ClipRightToTop](../Source/Action/ClipRightToTop.asm) |
| E1 | A5 | 15 | C08A | [ClipRightToBottomRight](../Source/Action/ClipRightToBottomRight.asm) |
| E1 | 69 | 19 | C12B | [ClipRightToTopRight](../Source/Action/ClipRightToTopRight.asm) |
| E1 | 96 | 16 | C101 | [ClipRightToBottomLeft](../Source/Action/ClipRightToBottomLeft.asm) |
| E1 | 5A | 1A | C132 | [ClipRightToTopLeft](../Source/Action/ClipRightToTopLeft.asm) |
| D2 | F0 | 20 | C144 | [ClipLeftToInside](../Source/Action/ClipLeftToInside.asm) |
| D2 | E1 | 21 | C14A | [ClipLeftToRight](../Source/Action/ClipLeftToRight.asm) |
| D2 | D2 | 22 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| D2 | B4 | 24 | C150 | [ClipLeftToBottom](../Source/Action/ClipLeftToBottom.asm) |
| D2 | 78 | 28 | C17B | [ClipLeftToTop](../Source/Action/ClipLeftToTop.asm) |
| D2 | A5 | 25 | C162 | [ClipLeftToBottomRight](../Source/Action/ClipLeftToBottomRight.asm) |
| D2 | 69 | 29 | C18D | [ClipLeftToTopRight](../Source/Action/ClipLeftToTopRight.asm) |
| D2 | 96 | 26 | C174 | [ClipLeftToBottomLeft](../Source/Action/ClipLeftToBottomLeft.asm) |
| D2 | 5A | 2A | C0D8 | [ClipLeftToTopLeft](../Source/Action/ClipLeftToTopLeft.asm) |
| B4 | F0 | 40 | C1A5 | [ClipBottomToInside](../Source/Action/ClipBottomToInside.asm) |
| B4 | E1 | 41 | C1AB | [ClipBottomToRight](../Source/Action/ClipBottomToRight.asm) |
| B4 | D2 | 42 | C1BD | [ClipBottomToLeft](../Source/Action/ClipBottomToLeft.asm) |
| B4 | B4 | 44 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| B4 | 78 | 48 | C1D6 | [ClipBottomToTop](../Source/Action/ClipBottomToTop.asm) |
| B4 | A5 | 45 | C1CF | [ClipBottomToBottomRight](../Source/Action/ClipBottomToBottomRight.asm) |
| B4 | 69 | 49 | C1DC | [ClipBottomToTopRight](../Source/Action/ClipBottomToTopRight.asm) |
| B4 | 96 | 46 | C0A4 | [ClipBottomToBottomLeft](../Source/Action/ClipBottomToBottomLeft.asm) |
| B4 | 5A | 4A | C1F1 | [ClipBottomToTopLeft](../Source/Action/ClipBottomToTopLeft.asm) |
| 78 | F0 | 80 | C30E | [ClipTopToInside](../Source/Action/ClipTopToInside.asm) |
| 78 | E1 | 81 | C314 | [ClipTopToRight](../Source/Action/ClipTopToRight.asm) |
| 78 | D2 | 82 | C326 | [ClipTopToLeft](../Source/Action/ClipTopToLeft.asm) |
| 78 | B4 | 84 | C338 | [ClipTopToBottom](../Source/Action/ClipTopToBottom.asm) |
| 78 | 78 | 88 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| 78 | A5 | 85 | C33E | [ClipTopToBottomRight](../Source/Action/ClipTopToBottomRight.asm) |
| 78 | 69 | 89 | C0BE | [ClipTopToTopRight](../Source/Action/ClipTopToTopRight.asm) |
| 78 | 96 | 86 | C359 | [ClipTopToBottomLeft](../Source/Action/ClipTopToBottomLeft.asm) |
| 78 | 5A | 8A | C36E | [ClipTopToTopLeft](../Source/Action/ClipTopToTopLeft.asm) |
| A5 | F0 | 50 | C20C | [ClipBottomRightToInside](../Source/Action/ClipBottomRightToInside.asm) |
| A5 | E1 | 51 | C228 | [ClipBottomRightToRight](../Source/Action/ClipBottomRightToRight.asm) |
| A5 | D2 | 52 | C22F | [ClipBottomRightToLeft](../Source/Action/ClipBottomRightToLeft.asm) |
| A5 | B4 | 54 | C24E | [ClipBottomRightToBottom](../Source/Action/ClipBottomRightToBottom.asm) |
| A5 | 78 | 58 | C25F | [ClipBottomRightToTop](../Source/Action/ClipBottomRightToTop.asm) |
| A5 | A5 | 55 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| A5 | 69 | 59 | C6EA | [ExitClipContour](../Source/Action/ExitClipContour.asm) |
| A5 | 96 | 56 | C259 | [ClipBottomRightToBottomLeft](../Source/Action/ClipBottomRightToBottomLeft.asm) |
| A5 | 5A | 5A | C274 | [ClipBottomRightToTopLeft](../Source/Action/ClipBottomRightToTopLeft.asm) |
| 69 | F0 | 90 | C375 | [ClipTopRightToInside](../Source/Action/ClipTopRightToInside.asm) |
| 69 | E1 | 91 | C391 | [ClipTopRightToRight](../Source/Action/ClipTopRightToRight.asm) |
| 69 | D2 | 92 | C39C | [ClipTopRightToLeft](../Source/Action/ClipTopRightToLeft.asm) |
| 69 | B4 | 94 | C3B1 | [ClipTopRightToBottom](../Source/Action/ClipTopRightToBottom.asm) |
| 69 | 78 | 98 | C3EF | [ClipTopRightToTop](../Source/Action/ClipTopRightToTop.asm) |
| 69 | A5 | 95 | C3D0 | [ClipTopRightToBottomRight](../Source/Action/ClipTopRightToBottomRight.asm) |
| 69 | 69 | 99 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| 69 | 96 | 96 | C3D6 | [ClipTopRightToBottomLeft](../Source/Action/ClipTopRightToBottomLeft.asm) |
| 69 | 5A | 9A | C6EA | [ExitClipContour](../Source/Action/ExitClipContour.asm) |
| 96 | F0 | 60 | C28D | [ClipBottomLeftToInside](../Source/Action/ClipBottomLeftToInside.asm) |
| 96 | E1 | 61 | C2A9 | [ClipBottomLeftToRight](../Source/Action/ClipBottomLeftToRight.asm) |
| 96 | D2 | 62 | C2BE | [ClipBottomLeftToLeft](../Source/Action/ClipBottomLeftToLeft.asm) |
| 96 | B4 | 64 | C2C9 | [ClipBottomLeftToBottom](../Source/Action/ClipBottomLeftToBottom.asm) |
| 96 | 78 | 68 | C2D0 | [ClipBottomLeftToTop](../Source/Action/ClipBottomLeftToTop.asm) |
| 96 | A5 | 65 | C6EA | [ExitClipContour](../Source/Action/ExitClipContour.asm) |
| 96 | 69 | 69 | C2EF | [ClipBottomLeftToTopRight](../Source/Action/ClipBottomLeftToTopRight.asm) |
| 96 | 96 | 66 | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |
| 96 | 5A | 6A | C308 | [ClipBottomLeftToTopLeft](../Source/Action/ClipBottomLeftToTopLeft.asm) |
| 5A | F0 | A0 | C3F6 | [ClipTopLeftToInside](../Source/Action/ClipTopLeftToInside.asm) |
| 5A | E1 | A1 | C412 | [ClipTopLeftToRight](../Source/Action/ClipTopLeftToRight.asm) |
| 5A | D2 | A2 | C431 | [ClipTopLeftToLeft](../Source/Action/ClipTopLeftToLeft.asm) |
| 5A | B4 | A4 | C438 | [ClipTopLeftToBottom](../Source/Action/ClipTopLeftToBottom.asm) |
| 5A | 78 | A8 | C466 | [ClipTopLeftToTop](../Source/Action/ClipTopLeftToTop.asm) |
| 5A | A5 | A5 | C44D | [ClipTopLeftToBottomRight](../Source/Action/ClipTopLeftToBottomRight.asm) |
| 5A | 69 | A9 | C471 | [ClipTopLeftToTopRight](../Source/Action/ClipTopLeftToTopRight.asm) |
| 5A | 96 | A6 | C6EA | [ExitClipContour](../Source/Action/ExitClipContour.asm) |
| 5A | 5A | AA | C07A | [ReturnClipCase](../Source/Action/ReturnClipCase.asm) |

Сборка, IRQ, нативный запуск, полные договоры обработчиков и всех входных профилей не проверялись.

[Все 241 пути и численная проверка](ActionClipCases.md) описаны отдельно, границы полноты проверки сохранены явно.
