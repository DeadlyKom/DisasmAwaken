# Физические параметры вступления

Данные выделены из секторного содержимого AWAKEN.B. Адреса относятся к
загруженному вступлению, где файловому смещению 0100 соответствует 6400.
Логическая BASIC-программа заканчивается раньше и эти адреса не задаёт.
Исходные значения, адреса и порядок байтов сохранены.

| Адрес | Размер | Источник | Потребитель |
|---|---:|---|---|
| 6615 | 9 | [StationFileKey](../Source/Intro/Data/StationFileKey.asm) | [LoadStation](../Source/Intro/LoadStation.asm) |
| 662C | 12 | [FinalTexturePhases](../Source/Intro/Data/FinalTexturePhases.asm) | [DrawFinalTextureFrame](../Source/Intro/DrawFinalTextureFrame.asm) |
| 6663 | 64 | [AlternatingLookup](../Source/Intro/Data/AlternatingLookup.asm) | [BuildAlternatingTexture](../Source/Intro/BuildAlternatingTexture.asm), первые 63 байта |
| 6993 | 16 | [AttributeNibbleSeeds](../Source/Intro/Data/AttributeNibbleSeeds.asm) | [BuildAttributeWriter](../Source/Intro/BuildAttributeWriter.asm) |
| 6B73 | 32 | [ColumnTailSamples](../Source/Intro/Data/ColumnTailSamples.asm) | [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) |
| 6C62 | 40 | [ScaleCycle](../Source/Intro/Data/ScaleCycle.asm) | [AdvanceTextureScale](../Source/Intro/AdvanceTextureScale.asm) |

Ключ файла содержит восемь букв STATIONF и байт типа C. Это существующий
FTrDosFileKey, девять байтов без нулевого терминатора. LoadStation копирует
их в рабочее поле TR-DOS 5CDD перед поиском. Сам загрузчик исполняется после
переноса, однако его абсолютный указатель продолжает обращаться к 6615.

Две записи FTexturePhase начинаются с Phase=8000, Step=0, StepDelta=0.
Они передаются DrawScrolledTexture и обновляются AdvanceParameters.
Нулевые приращения оставляют обе исходные фазы неподвижными. Это реальные
экземпляры уже существующей структуры, не отдельные массивы слов.

BuildTextureLookup читает ровно 63 байта от 6663. Каждый задаёт начальный
IYL очередной последовательности. В варианте BuildAlternatingTexture
внутренний LD IYL,A сохраняется, значения становятся вторыми байтами
записей построенной таблицы. Последний отсчёт `P3F=#29` по `#66A2`
лежит за границей этих чтений. Все 64 байта совпадают с таблицей `IM_IT`
в `TUNEL.a`, `HIPER.a` и `DOOM.a`, а также в распакованных `EFF.c`
и `EFF1.c` из `awk1.trd`. У `EFF1.c` совпадают и соседние команды
до и после таблицы с поправкой на абсолютные адреса.
[Авторский архив](https://opensourcezx.untergrund.net/a_games-awaken_src.html) ·
[Проверка](../Tools/Disasm/Research/CheckIntroArchivedLookup.py) ·
[Сверка 64 байтов](../Tools/Disasm/Reports/IntroArchivedLookupVerification.json)

В первом вызове BuildIntroTexture
получает указатель #6080 от BuildScreenTables. Чтение 63 байтов сохраняется,
но вместо присваивания IYL выполняется INC IYL. Счётчик проходит от #C1
до #FF после начального #C0. В четырёх опытах менялись все 63 входных
байта. Содержимое итоговых 32 КиБ совпало для INC IYL и различалось для
LD IYL,A. [Сравнение вариантов](../Tools/Disasm/Reports/IntroVerification.json).

Исходный байт #66A2 переносится по #5E26 вместе с загрузчиком,
там чтений не обнаружено. Кроме этого переноса, он читается при
широком копировании строк BuildIntroTexture и попадает в #DCE2
банка 1. До чтения его заменяет #FF при заполнении для следующей
текстуры. Обе копии прослежены в четырёх профилях оригинального
вступления. [Трасса](../Tools/Disasm/Reports/IntroStationTransitionVerification.json).

Два набора по восемь байтов 6993 и 699B используются отдельно. Матрица
строки r и столбца c получается как `(source[c] & F0) | (source[r] & 0F)`.
Схема разрядов 7..0 имеет вид `CCCC RRRR`, старшая тетрада даёт верхнюю
часть атрибута столбца, младшая даёт нижнюю часть атрибута строки.
Это упакованные числовые части, а не восемь независимых флагов.
Нулевой байт даёт обе нулевые части. Начальные значения не считаются
неизменными, [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm)
и InitializeColumnEffect записывают ноль в первый байт первого набора.

Хвост из 32 кодов копируется в E0..FF каждой из 32 страниц от DAE0.
После выборки к коду прибавляются две фазовые добавки, затем выполняются
косвенные чтения в [ColumnSample](../Source/IntroTemplates/ColumnSample.asm).
Начальные коды C7..C1 не переименованы в самостоятельные адреса или цвета,
их полный смысл зависит от фаз и созданных таблиц.

Цикл масштаба содержит 40 числовых добавок 0..15. AdvanceTextureScale
сначала увеличивает индекс с оборачиванием по 40, выбирает добавку,
прибавляет 56 и передаёт индекс селектору строки указателей. При нулевой
добавке выбирается базовый индекс 56. Все разряды относятся к числу,
независимые флаги не назначаются. [Алгоритм масштаба](IntroTextureScale.md)
описывает также начальную ветвь нарастания.

[Проверка](../Tools/Disasm/Research/CheckIntroPhysicalParameters.py) сравнивает
173 исходных байта и выполняет шесть сценариев реальных читателей фаз и
матриц. Матрицы рассчитаны независимо для обоих наборов и варианта с
обнулением первого байта. Это не полная инициализация, не сборка и не
нативный запуск. Полная подготовка хвостов разобрана отдельно в
[эффектах вступления](IntroGeneratedEffects.md).
