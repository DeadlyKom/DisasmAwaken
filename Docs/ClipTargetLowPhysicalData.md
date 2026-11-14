# Младшая страница диспетчера и наложенные рабочие записи

Физические записи младших адресов занимают 444 байта, по 222 в ACTION
и 3DPART. Диспетчер читает CF00+I и D000+I, где
`I = ((NOT First.ClipCode) AND F0) OR (Second.ClipCode AND 0F)`.
Координаты, произведения и адресные ячейки имеют отдельные структуры.

| CPU-адреса | ACTION | 3DPART | Тип |
|---|---|---|---|
| CF08..CF0A | [ClipTargetLowAlias](../Source/Action/Data/ClipTargetLowAlias.asm) | [ClipTargetLowAlias](../Source/ThreeD/Data/ClipTargetLowAlias.asm) | FClipTargetLowAlias, три младших байта |
| CF10..CF1A | [ClipTargetLowRow1](../Source/Action/Data/ClipTargetLowRow1.asm) | [ClipTargetLowRow1](../Source/ThreeD/Data/ClipTargetLowRow1.asm) | FClipTargetLowHead, 11 байтов |
| CF20..CF2A | [ClipTargetLowRow2](../Source/Action/Data/ClipTargetLowRow2.asm) | [ClipTargetLowRow2](../Source/ThreeD/Data/ClipTargetLowRow2.asm) | FClipTargetLowHead, 11 байтов |
| CF3B..CF3F | [ClipTargetLowTail3](../Source/Action/Data/ClipTargetLowTail3.asm) | [ClipTargetLowTail3](../Source/ThreeD/Data/ClipTargetLowTail3.asm) | FClipTargetLowTail, 5 байтов |
| CF40..CFFF | [ClipTargetLowRows4F](../Source/Action/Data/ClipTargetLowRows4F.asm) | [ClipTargetLowRows4F](../Source/ThreeD/Data/ClipTargetLowRows4F.asm) | 12 FClipTargetLowRow по 16 байтов |

В полном FClipTargetLowRow поля SecondSides0..SecondSidesF имеют смещения 0..15. В FClipTargetLowHead остаются поля 0..A с теми же смещениями 0..10. Частичный FClipTargetLowTail начинается непосредственно по CF3B, поэтому его SecondSidesB..SecondSidesF имеют физические смещения 0..4, а не 11..15. Метка First3Tail обозначает начало этого хвоста, не начало строки CF30.

Для 150 ячеек двух копий установлены нормальные цели. Инициализаторы записаны через LOW от имён реальных обработчиков, например LOW(@Action.ClipRightToInside.Entry). Остальные 294 байта этих фрагментов исходно равны нулю и имеют индексы вне 81 нормальной пары. Их формат чтения установлен, но допустимость игровых переходов с такими кодами не доказана. Нулевое заполнение не используется как доказательство свободной памяти или отсутствия потребителя.

## Полная физическая разметка CF00..CFFF

| Диапазон | Байтов | Фактическая запись |
|---|---|---|
| CF00..CF07 | 8 | [Шесть младших адресных байтов, CornerBlock и SeenFlags](ClipDispatchPrefixData.md) |
| CF08..CF0A | 3 | Младшие байты целей для индексов 08, 09 и 0A, возможный вход исполнения разобран [отдельно](ActionClipTableAlias.md) |
| CF0B..CF0F | 5 | [Первая точка ACTION](../Source/Action/Data/ClipFirstPoint.asm), [первая точка 3DPART](../Source/ThreeD/Data/ClipFirstPoint.asm) |
| CF10..CF1A | 11 | Младшие адреса строки 1 |
| CF1B..CF1F | 5 | [Вторая точка ACTION](../Source/Action/Data/ClipSecondPoint.asm), [вторая точка 3DPART](../Source/ThreeD/Data/ClipSecondPoint.asm) |
| CF20..CF2A | 11 | Младшие адреса строки 2 |
| CF2B..CF3A | 16 | [Произведения ACTION](../Source/Action/Data/ClipProducts.asm), [произведения 3DPART](../Source/ThreeD/Data/ClipProducts.asm) |
| CF3B..CF3F | 5 | Сохраняемый адресный хвост строки 3 |
| CF40..CFFF | 192 | Полные строки 4..F |

Сумма равна 256 байтам. Рабочие записи наложены на индексы, которые не образуются из девяти нормальных кодов положения. Их изменение не повреждает адреса 81 нормальной пары. Это свойство конкретного договора, а не доказательство безопасности произвольных байтов ClipCode.

Страницу [старших адресов D000](PolygonFillPhysicalData.md) следует читать совместно с этой разметкой. Нельзя заменять все 256 младших байтов одними постоянными указателями, это уничтожило бы рабочие структуры. Нельзя также считать три байта CF08 готовой подтверждённой процедурой только из-за декодирования DI, XOR A, RET, см. [границу доказательства](ActionClipTableAlias.md).

Реальные потребители, [ClipPolygon ACTION](../Source/Action/ClipPolygon.asm), [ClipSingleEdge ACTION](../Source/Action/ClipSingleEdge.asm), [ClipPolygon 3DPART](../Source/ThreeD/ClipPolygon.asm) и [ClipSingleEdge 3DPART](../Source/ThreeD/ClipSingleEdge.asm), сохраняют исходный алгоритм вычисления индекса и последующего косвенного перехода. Имена новых структур не доказывают новые игровые пути.

## Проверка

[Описание записей и обратимый разбор LOW](../Tools/Disasm/Research/ClipTargetLowPhysicalData.py), [публикация кандидата](../Tools/Disasm/Research/PublishPhysicalDataTables.py), [отчёт](../Tools/Disasm/Reports/ClipTargetLowPhysicalDataClassification.json). Проверяются все 444 байта, 32 физические записи, 476 имён, размеры и смещения четырёх STRUCT. Для 150 нормальных ячеек обе части указателя сравниваются с исходным реестром целей. По CF08 обе копии сохраняют F3 AF C9.

Синтаксис LOW является оператором [SjASMPlus](https://z00m128.github.io/sjasmplus/#s_expressions). Статическая проверка вычисляет его только для известных глобальных имён и сравнивает с оригиналом. Игровой вход исполнения по CF08..CF0A, сборка и нативный запуск нового оформления остаются за границей проверки.
