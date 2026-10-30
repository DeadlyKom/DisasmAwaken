# Исходные операнды и настроенное состояние карты

Исходный образ и выполняемый код имеют разные фазы. Проверенные ранее модели отдельных помощников начинались с байтов образа. Их формулы 0/255, порог Y=192 и колонки 1/30 верны для этого состояния. [Установщик D0C3](../Source/Map/SetupMapRasterWindow.asm) меняет 69 байтов, включая операнды этих помощников. Запуск такой модели без установщика не доказывает настроенный игровой профиль.

## Установленные записи

| Группа | Исходное состояние | После D0C3 |
| --- | --- | --- |
| Классификатор X/Y | CP FF | CP ((MaxX+1)&255), CP ((MaxY+1)&255) |
| Четыре произведения | границы 0/255 | MinY, MaxY, MinX, MaxX |
| Угловые пары | 0/255 | четыре пары Min/Max |
| Пересечения | фиксированные координаты и порог Y=192 | соответствующие Min/Max, порог сравнения Y остаётся 192 |
| Левая и правая колонки дуги | 1 и 30 | ColumnByte[0] и ColumnByte[MaxX] |
| Колонка поиска строки | исходный OR 0 | OR ColumnByte[MaxX] |

Дисковый профиль нельзя свести к одному согласованному прямоугольнику. Исходный классификатор исключает 255, а неподготовленный проектор Y сравнивает с 192 и при отказе записывает 255. Установщик меняет координаты и значения насыщения на параметры окна. Порог сравнения Y=192 остаётся прежним, байтовая арифметика и оборачивания сохранены.

HL установщика передаёт MaxY:MaxX, DE — MinY:MinX. Известный вызывающий код задаёт DE=0. Классификатор продолжает проверять отрицательность относительно нуля, а не произвольного ненулевого Min, поэтому механическое копирование ненулевого DE ещё не доказывает геометрическую корректность такого окна. Новых проверок в исходный код не добавлено.

## Половины размеров и перенос

Установщик вычисляет HalfX=((MaxX+1)&255) SHR 1. После записи части полей выполняется SUB 2, затем LD A,H и RRA без предварительной очистки Carry. Поэтому HalfY=(((MaxY+1)&255) SHR 1) OR (128 при HalfX<2). Это фактическая связь через перенос, она сохранена. Простая независимая формула половины Y была бы неверна для коротких и оборачиваемых размеров.

[Модель установщика](../Tools/Disasm/Research/CheckMapRasterSetup.py) проверила 131 072 случая, все пары верхних и все пары нижних байтовых границ. [Отчёт](../Tools/Disasm/Reports/MapRasterSetupVerification.json) подтверждает каждую из 69 записываемых позиций и регистры. В 1024 случаях установлен старший бит HalfY из-за предшествующего SUB. Это проверка механики установщика, геометрическая корректность всех входов и исполнение настроенных потребителей ею не заявлены.

## Изменяемые условия масок дуги

[Основное ядро DFC3](../Source/Map/DrawClippedMapArc.asm) выбирает 38 или 30 и записывает коды четырёх JR по E426, E438, E44F, E460. Это переключает поиск установленного либо сброшенного бита. [Расширенная модель хвостов](ArcClosing.md) проверяет оба состояния, JR C и JR NC имеют разные формулы. Проверены 393728 случаев и настоящий писатель четырёх кодов для всех 256 параметров DFC4. [Рекуррентное ядро](ArcKernel.md) описано отдельно, диспетчер DFC3 описан в [ArcDispatcher](ArcDispatcher.md).

[Каталог прямых писателей](../Tools/Disasm/Reports/MapRuntimeWrites.json) связывает каждую запись с фактическим байтом инструкции либо данных. Каталог не утверждает полноты всех косвенных писателей игры. Сборка и нативный запуск не выполнялись.

## Проверенные договоры и границы

Настроенный профиль проверен для следующих исходников. Их договоры различают исходные значения операндов и записи SetupMapRasterWindow:

- [BuildMapPointOutcodes](../Source/Map/BuildMapPointOutcodes.asm).
- [ComputeTopClipProduct](../Source/Map/ComputeTopClipProduct.asm), [ComputeBottomClipProduct](../Source/Map/ComputeBottomClipProduct.asm), [ComputeLeftClipProduct](../Source/Map/ComputeLeftClipProduct.asm), [ComputeRightClipProduct](../Source/Map/ComputeRightClipProduct.asm).
- [AppendTopClipIntersection](../Source/Map/AppendTopClipIntersection.asm), [AppendBottomClipIntersection](../Source/Map/AppendBottomClipIntersection.asm), [AppendLeftClipIntersection](../Source/Map/AppendLeftClipIntersection.asm), [AppendRightClipIntersection](../Source/Map/AppendRightClipIntersection.asm).
- [AppendTopLeftCorner](../Source/Map/AppendTopLeftCorner.asm), [AppendTopRightCorner](../Source/Map/AppendTopRightCorner.asm), [AppendBottomLeftCorner](../Source/Map/AppendBottomLeftCorner.asm), [AppendBottomRightCorner](../Source/Map/AppendBottomRightCorner.asm).
- [PrepareArcLeftEdge](../Source/Map/PrepareArcLeftEdge.asm), [PrepareArcRightEdge](../Source/Map/PrepareArcRightEdge.asm), [ResetRasterSpanEdges](../Source/Map/ResetRasterSpanEdges.asm).
- [SeekRasterRowUp](../Source/Map/SeekRasterRowUp.asm), [SeekRasterRowDown](../Source/Map/SeekRasterRowDown.asm).

| Семейство | Случаев после настройки | Модель |
| --- | --- | --- |
| Классификатор | 331776 | [Пороги и заголовки](../Tools/Disasm/Research/CheckConfiguredMapOutcodes.py) |
| Произведения | 303104 | [Границы и множители](../Tools/Disasm/Research/CheckConfiguredClipProducts.py) |
| Пересечения | 142946 | [Полный и кэшированный входы](../Tools/Disasm/Research/CheckClipIntersections.py), `--configured` |
| Углы | 523264 | [Запрет и курсор](../Tools/Disasm/Research/CheckConfiguredClipCorners.py) |
| Подготовки дуги | 327680 | [Колонки и смещения](../Tools/Disasm/Research/CheckArcPreparation.py), `--configured` |
| Сброс пролёта | 63488 | [Настроенные растровые помощники](../Tools/Disasm/Research/CheckConfiguredRasterSeek.py) |
| Поиск строки | 377344 | Та же модель, оба направления |

Каждая модель выполняет настоящий установщик, не подменяет вызовы и проверяет точные регистры и флаги. Наборы параметров перечислены в профильной документации, полный декартов перебор всех параметров не заявляется. Геометрический договор поиска ограничен колонками 0..31 и различающимися границами, выровненными по восьми строкам. При таблицах с входным DE=0 MaxX=248..255 даёт колонку 32 и выходит за этот договор. MinX/MinY не сдвигают нулевую нижнюю границу классификатора. Эти ограничения сохранены в исходниках.

Проверка 18 отдельных потребителей дополняется [случаями отсечения](ClipCases.md) и [диспетчером дуги](ArcDispatcher.md). Достижимость всех модельных входов в игре не доказана. Сборка, IRQ и нативный запуск этими проверками не выполнялись.
