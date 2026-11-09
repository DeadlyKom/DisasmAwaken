# Физические таблицы диспетчера и заливки

Оформлены 852 исходных байта, 202 физических записи и 1054 имени. Это две старшие страницы адресного диспетчера по 256 байтов, две копии пяти пар шаблонов по десять байтов и 320 разреженных байтов крайних масок. Исходные адреса и байты не изменяются, новая память не выделяется.

## Старшие части адресов

[ActionClipTargetHigh](../Source/Action/Data/ClipTargetHigh.asm) находится в ACTION, файловые смещения 7000..70FF. [ThreeDClipTargetHigh](../Source/ThreeD/Data/ClipTargetHigh.asm) находится в 3DPART, смещения 1000..10FF. В соответствующем загруженном оверлее обе страницы имеют CPU-адреса D000..D0FF. Это разные дисковые копии одного формата.

Диспетчер вычисляет индекс I=((NOT First.ClipCode) AND F0) OR (Second.ClipCode AND 0F), читает младший адресный байт из CF00+I и старший из D000+I. Поэтому старшая страница оформлена шестнадцатью FClipTargetHighRow по шестнадцать физических байтов. FirstSides0..FirstSidesF соответствуют старшей тетраде индекса, SecondSides0..SecondSidesF выбираются младшей тетрадой. Для нормального парного кода старшая тетрада индекса равна сторонам первой точки, младшая сторонам второй.

[81 нормальная пара](../Tools/Disasm/Reports/ActionClipDispatchTable.json) имеет установленные адреса и обработчики. Для каждой такой ячейки инициализатор использует HIGH от имени функции соответствующей копии, например HIGH(@Action.ClipInsideToRight.Entry). Статический разбор получает значение из проверяемого реестра символов и сверяет его с исходным байтом, это не запуск ассемблера. Синтаксис HIGH соответствует [документации SjASMPlus](https://z00m128.github.io/sjasmplus/#s_expressions).

Оставшиеся 175 старших байтов каждой копии исходно равны нулю. Такие индексы не образуются из девяти нормальных ClipCode. Их ячейки всё равно принадлежат странице, которую индексирует исходный код, и сохранены в своём физическом положении. Они не объявляются свободными, неиспользуемыми или допустимыми игровыми переходами. Формат чтения установлен, возможные роли за пределами нормального договора и полный граф косвенного исполнения не доказаны.

[ClipPolygon ACTION](../Source/Action/ClipPolygon.asm), [ClipSingleEdge ACTION](../Source/Action/ClipSingleEdge.asm), [ClipPolygon 3DPART](../Source/ThreeD/ClipPolygon.asm) и [ClipSingleEdge 3DPART](../Source/ThreeD/ClipSingleEdge.asm) используют соответствующую страницу вместе с младшей CF00. Спорные CF08..CF0A не переклассифицированы, см. [табличную роль и неизвестный вход](ActionClipTableAlias.md).

## Пять пар шаблонов

[ActionPolygonPatterns](../Source/Action/Data/PolygonPatterns.asm) и [ThreeDPolygonPatterns](../Source/ThreeD/Data/PolygonPatterns.asm) занимают D100..D109 в соответствующей копии. Каждая содержит Mode0..Mode4 существующего типа FPreviewFillPattern. Его формат совпадает с данным алгоритмом, отдельный дублирующий тип не вводится.

| Режим | Pattern первой строки | RowXor | Шаблон следующей строки |
|---|---|---|---|
| 0 | FF | 00 | FF |
| 1 | 77 | AA | DD |
| 2 | 55 | FF | AA |
| 3 | 11 | 55 | 44 |
| 4 | 00 | 00 | 00 |

RowXor прибавляется по XOR к текущему шаблону после каждой строки. Начало чередования устанавливается на первой строке данного контура, оно не определяется чётностью абсолютной координаты Y. Нулевой шаблон режима 4 не означает прозрачность, покрытые пиксели могут очищаться.

[PreparePolygonFill ACTION](../Source/Action/PreparePolygonFill.asm) и [PreparePolygonFill 3DPART](../Source/ThreeD/PreparePolygonFill.asm) выбирают пару по D100+2*Mode. Pattern попадает в альтернативный A, RowXor записывается в два существующих операнда строкового ядра. Прежний ActionPolygonPreparationState.Patterns остаётся числовым EQU с ASSERT связи с физическим ActionPolygonPatterns.Mode0.Pattern.

## Разреженные крайние маски

Маски находятся в общей фиксированной RAM 8C00..8DFF, физически в ACTION, а не в отдельной странице каждого оверлея. Оформлены только 320 подтверждённых байтов. Между пятёрками двухбайтовых записей сохранены исходные промежутки, в них находятся также рабочие точки и коды режима линии. Эти промежутки не подставляются как вычисленные маски и не объявляются пустыми.

Каждая FPolygonEdgeMask содержит Preserve по смещению 0 и Apply по смещению 1. Пара применяется как result=(old AND Preserve) OR Apply. Биты 7..0 соответствуют пикселям байта слева направо, маски пикселей 80, 40, 20, 10, 08, 04, 02, 01. Единица Preserve сохраняет прежний пиксель, единица Apply устанавливает пиксель шаблона. Для исходных масок Preserve AND Apply равен нулю.

Preserve=00 не сохраняет ни одного старого пикселя, Preserve=FF с Apply=00 сохраняет весь байт. Apply=00 не означает отсутствие воздействия, биты с нулевым Preserve очищаются. Поэтому общий нулевой байт нельзя трактовать как пустую либо неиспользуемую ячейку.

Обозначим P чётность смещения строки относительно первой строки контура, X горизонтальную координату границы, phase=X AND 7, M режим 0..4. Адрес пары равен 8C00+256*P+32*phase+2*M для левой границы и ещё плюс 16 для правой. При P=0 шаблон равен Pattern, при P=1 равен Pattern XOR RowXor.

Для левой границы Preserve=(FF SHL (8-phase)) AND FF, для правой Preserve=FF SHR phase. В обоих случаях Apply=шаблон AND NOT Preserve. Названия Even и Odd в файлах означают P=0 и P=1 относительно контура, не абсолютную экранную строку.

| Фаза X | Even слева | Even справа | Odd слева | Odd справа |
|---|---|---|---|---|
| 0 | [8C00](../Source/Action/Data/PolygonMasks/EvenLeft0.asm) | [8C10](../Source/Action/Data/PolygonMasks/EvenRight0.asm) | [8D00](../Source/Action/Data/PolygonMasks/OddLeft0.asm) | [8D10](../Source/Action/Data/PolygonMasks/OddRight0.asm) |
| 1 | [8C20](../Source/Action/Data/PolygonMasks/EvenLeft1.asm) | [8C30](../Source/Action/Data/PolygonMasks/EvenRight1.asm) | [8D20](../Source/Action/Data/PolygonMasks/OddLeft1.asm) | [8D30](../Source/Action/Data/PolygonMasks/OddRight1.asm) |
| 2 | [8C40](../Source/Action/Data/PolygonMasks/EvenLeft2.asm) | [8C50](../Source/Action/Data/PolygonMasks/EvenRight2.asm) | [8D40](../Source/Action/Data/PolygonMasks/OddLeft2.asm) | [8D50](../Source/Action/Data/PolygonMasks/OddRight2.asm) |
| 3 | [8C60](../Source/Action/Data/PolygonMasks/EvenLeft3.asm) | [8C70](../Source/Action/Data/PolygonMasks/EvenRight3.asm) | [8D60](../Source/Action/Data/PolygonMasks/OddLeft3.asm) | [8D70](../Source/Action/Data/PolygonMasks/OddRight3.asm) |
| 4 | [8C80](../Source/Action/Data/PolygonMasks/EvenLeft4.asm) | [8C90](../Source/Action/Data/PolygonMasks/EvenRight4.asm) | [8D80](../Source/Action/Data/PolygonMasks/OddLeft4.asm) | [8D90](../Source/Action/Data/PolygonMasks/OddRight4.asm) |
| 5 | [8CA0](../Source/Action/Data/PolygonMasks/EvenLeft5.asm) | [8CB0](../Source/Action/Data/PolygonMasks/EvenRight5.asm) | [8DA0](../Source/Action/Data/PolygonMasks/OddLeft5.asm) | [8DB0](../Source/Action/Data/PolygonMasks/OddRight5.asm) |
| 6 | [8CC0](../Source/Action/Data/PolygonMasks/EvenLeft6.asm) | [8CD0](../Source/Action/Data/PolygonMasks/EvenRight6.asm) | [8DC0](../Source/Action/Data/PolygonMasks/OddLeft6.asm) | [8DD0](../Source/Action/Data/PolygonMasks/OddRight6.asm) |
| 7 | [8CE0](../Source/Action/Data/PolygonMasks/EvenLeft7.asm) | [8CF0](../Source/Action/Data/PolygonMasks/EvenRight7.asm) | [8DE0](../Source/Action/Data/PolygonMasks/OddLeft7.asm) | [8DF0](../Source/Action/Data/PolygonMasks/OddRight7.asm) |

Каждый из этих файлов содержит пять физических Mode0..Mode4 без заполнения соседнего промежутка. [PolygonFillRows ACTION](../Source/Action/PolygonFillRows.asm) и [PolygonFillRows 3DPART](../Source/ThreeD/PolygonFillRows.asm) используют общие маски. Сведение обеих границ в один байт имеет отдельную формулу объединения, см. [полный алгоритм](ActionPolygonFill.md) и [строковое ядро](ActionPolygonFillRows.md).

## Проверка и пределы

Дополнительные индексы 5..7 и их перекрытие рабочими полями разобраны отдельно. [Физические пары ACTION](ActionPolygonExtraMaskPairs.md)

[Описание таблиц и обратимый разбор](../Tools/Disasm/Research/PolygonFillPhysicalData.py), [публикация отдельного кандидата](../Tools/Disasm/Research/PublishPhysicalDataTables.py), [отчёт](../Tools/Disasm/Reports/PolygonFillPhysicalDataClassification.json). VerifySources проверяет реальные STRUCT, все 852 байта, смещения, 1054 физических имени, адресную привязку и формулу каждой маски. Имена целей HIGH сопоставлены с 162 исходными адресами двух копий. Исходные инструкции не меняются.

Действуют результаты [проверки заливки](../Tools/Disasm/Reports/ActionPolygonFillBitmapVerification.json), 11562 сценария выпуклых контуров положительного обхода, режимы 0..4 и согласованные координаты. Все пиксели, физическая RAM и кратность записей покрыты этой моделью. Она не доказывает весь игровой процесс, все совместные входы, точное R/T, режимы 5..7 или допустимость произвольных кодов диспетчера. Сборка и нативный запуск новой разметки не выполнялись.

[Физическая разметка всей младшей страницы CF00](ClipTargetLowPhysicalData.md) сохраняет наложенные рабочие записи и отдельный Unknown CF08.
