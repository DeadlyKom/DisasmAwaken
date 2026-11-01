# Исходная композиция Antichrist

Композиция занимает 4137 байтов по E700..F728, файловые смещения 0C00..1C28 MUZ1.C. Все байты оформлены исходными директивами в 72 частях. Обычная сборка включает их непосредственно из Source/Files/10_MUZ1.inc средствами SjASMPlus, отдельный конвертер не требуется. Общие потоки не скопированы по числу ссылок, нулевые относительные адреса сохранены.

Строка описания буквально содержит ProTracker 3.6, Antichrist, SET/ELLiPSE GROUP и 01.11.2000. Эта строка сохранена целиком, включая исходные пробелы. Байты остаются источником истины, название формата не заменяет проверку поведения проигрывателя этой версии.

## Заголовок и таблицы относительных адресов

| Исходник | Смещение в композиции | Размер | Физическое содержание |
| --- | --- | ---: | --- |
| [Header](../Source/Music/Composition/Header.asm) | #0000 | 105 | FMusicModuleHeader, описание и исходные поля настройки |
| [SampleOffsets](../Source/Music/Composition/SampleOffsets.asm) | #0069 | 64 | 32 FMusicRelativePointer сэмплов |
| [OrnamentOffsets](../Source/Music/Composition/OrnamentOffsets.asm) | #00A9 | 32 | 16 FMusicRelativePointer орнаментов |
| [Positions](../Source/Music/Composition/Positions.asm) | #00C9 | 29 | 28 FMusicPositionByte и отдельный байт End=FF |
| [PatternOffsets](../Source/Music/Composition/PatternOffsets.asm) | #00E6 | 114 | 19 FMusicPatternPointers по три относительных слова |

FMusicModuleHeader имеет поля Description размером 99 байтов, Unknown63 по смещению 99, RowTempo по 100, PositionCount по 101, LoopIndex по 102 и слово PatternTable по 103. Итого 105 байтов. Значения настройки равны 3, 28, 4 и 230 соответственно. InitializeModule читает PositionCount в F через POP AF, но конец списка выбирает по FF, не по этому числу. LoopIndex=4 указывает пятый байт списка, а не номер группы паттернов.

Unknown63 содержит 02, инициализатор пропускает этот байт. Его назначение по фактическому потребителю не доказано, поэтому имя Unknown сохранено. Внешнее описание другой версии PT3 не используется как доказательство для этого байта.

FMusicRelativePointer.Offset отсчитывается от E700, InitializeModule добавляет эту базу и сохраняет абсолютные слова в [таблице проигрывателя](MusicPlayerData.md). Двадцать записей сэмплов и две записи орнаментов содержат нулевое слово. Алгоритм превращает его в E700, не в адрес EmptySample. Отдельные записи сэмпла или орнамента по этому адресу не создаются, там уже лежит заголовок.

Байты позиций равны 15, 18, 21, 24, 0, 3, 0, 27, 6, 9, 6, 12, 0, 3, 0, 27, 30, 33, 30, 36, 39, 42, 39, 45, 48, 51, 48, 54, затем FF. Все обычные значения кратны трём. [AdvancePatternA](MusicPattern.md) прибавляет удвоенный байт позиции к таблице, поэтому 15 выбирает шестую тройку, а 54 девятнадцатую. Сам код не умножает номер группы на шесть и не исправляет некратные значения.

Каждый FMusicPatternPointers содержит ChannelA, ChannelB, ChannelC со смещениями 0, 2 и 4. Это относительные слова. Повторяющиеся значения указывают общие физические потоки, а не отдельные копии с одинаковым содержимым.

## Физические потоки паттернов

Все 57 ссылок из девятнадцати троек сводятся к 41 физическому потоку. Границы проверены по адресам ссылок и собственному нулевому байту в конце каждого потока. Команды оформлены DB с русским пояснением каждой группы, RowXX обозначает начало очередной декодируемой строки. Это номер строки команд, не число кадров и не значение длительности.

Внутри строки отдельно выделены немедленные данные и параметры отложенных эффектов. Команды 05, 01 и 08 в композиции помещают обработчики в стек, параметры после ноты либо D0 читаются в порядке RET от последней команды к первой. Точная грамматика, отличие шумового диапазона B и все регистровые контракты приведены в [MusicPattern](MusicPattern.md), параметры эффектов в [MusicEffects](MusicEffects.md).

End=00 находится вне разобранных строк. Для A вызывающий код использует его как признак перехода позиции. У B/C тот же физический конечный байт не превращён в новую команду декодера, поступление на него как на обычную команду было бы чтением зарезервированного слова эффекта 00. Сценарий смены позиций не следует подменять универсальным правилом, что любой ноль завершает любой декодер.

| Исходник | Смещение | Байтов | Строк команд | Ссылки номер группы и канал |
| --- | --- | ---: | ---: | --- |
| [PatternA00](../Source/Music/Composition/Patterns/PatternA00.asm) | #0158 | 49 | 19 | 0A |
| [PatternA01](../Source/Music/Composition/Patterns/PatternA01.asm) | #0189 | 49 | 19 | 1A, 9A |
| [PatternA02](../Source/Music/Composition/Patterns/PatternA02.asm) | #01BA | 77 | 26 | 2A |
| [PatternA03](../Source/Music/Composition/Patterns/PatternA03.asm) | #0207 | 71 | 23 | 3A |
| [PatternA04](../Source/Music/Composition/Patterns/PatternA04.asm) | #024E | 71 | 23 | 4A |
| [PatternA05](../Source/Music/Composition/Patterns/PatternA05.asm) | #0295 | 33 | 11 | 5A |
| [PatternA06](../Source/Music/Composition/Patterns/PatternA06.asm) | #02B6 | 37 | 13 | 6A |
| [PatternA07](../Source/Music/Composition/Patterns/PatternA07.asm) | #02DB | 41 | 15 | 7A |
| [PatternA08](../Source/Music/Composition/Patterns/PatternA08.asm) | #0304 | 45 | 17 | 8A |
| [PatternA0A](../Source/Music/Composition/Patterns/PatternA0A.asm) | #0331 | 49 | 9 | 10A |
| [PatternA0B](../Source/Music/Composition/Patterns/PatternA0B.asm) | #0362 | 49 | 9 | 11A |
| [PatternA0C](../Source/Music/Composition/Patterns/PatternA0C.asm) | #0393 | 50 | 9 | 12A |
| [PatternA0D](../Source/Music/Composition/Patterns/PatternA0D.asm) | #03C5 | 69 | 32 | 13A |
| [PatternA0E](../Source/Music/Composition/Patterns/PatternA0E.asm) | #040A | 69 | 32 | 14A |
| [PatternA0F](../Source/Music/Composition/Patterns/PatternA0F.asm) | #044F | 74 | 32 | 15A |
| [PatternA10](../Source/Music/Composition/Patterns/PatternA10.asm) | #0499 | 36 | 6 | 16A |
| [PatternA11](../Source/Music/Composition/Patterns/PatternA11.asm) | #04BD | 36 | 6 | 17A |
| [PatternA12](../Source/Music/Composition/Patterns/PatternA12.asm) | #04E1 | 40 | 7 | 18A |
| [PatternB00](../Source/Music/Composition/Patterns/PatternB00.asm) | #0509 | 196 | 64 | 0B, 10B |
| [PatternB01](../Source/Music/Composition/Patterns/PatternB01.asm) | #05CD | 196 | 64 | 1B, 9B, 11B, 12B |
| [PatternB02](../Source/Music/Composition/Patterns/PatternB02.asm) | #0691 | 218 | 64 | 2B |
| [PatternB03](../Source/Music/Composition/Patterns/PatternB03.asm) | #076B | 214 | 64 | 3B, 4B |
| [PatternB05](../Source/Music/Composition/Patterns/PatternB05.asm) | #0841 | 21 | 5 | 5B |
| [PatternB06](../Source/Music/Composition/Patterns/PatternB06.asm) | #0856 | 21 | 5 | 6B |
| [PatternB07](../Source/Music/Composition/Patterns/PatternB07.asm) | #086B | 25 | 7 | 7B |
| [PatternB08](../Source/Music/Composition/Patterns/PatternB08.asm) | #0884 | 29 | 9 | 8B |
| [PatternB0D](../Source/Music/Composition/Patterns/PatternB0D.asm) | #08A1 | 9 | 2 | 13B |
| [PatternB0E](../Source/Music/Composition/Patterns/PatternB0E.asm) | #08AA | 9 | 2 | 14B, 15B |
| [PatternB10](../Source/Music/Composition/Patterns/PatternB10.asm) | #08B3 | 260 | 64 | 16B |
| [PatternB11](../Source/Music/Composition/Patterns/PatternB11.asm) | #09B7 | 260 | 64 | 17B |
| [PatternB12](../Source/Music/Composition/Patterns/PatternB12.asm) | #0ABB | 257 | 64 | 18B |
| [PatternC00](../Source/Music/Composition/Patterns/PatternC00.asm) | #0BBC | 106 | 20 | 0C, 2C, 10C, 16C |
| [PatternC01](../Source/Music/Composition/Patterns/PatternC01.asm) | #0C26 | 106 | 20 | 1C, 3C, 11C, 17C |
| [PatternC04](../Source/Music/Composition/Patterns/PatternC04.asm) | #0C90 | 101 | 20 | 4C, 9C, 12C, 18C |
| [PatternC05](../Source/Music/Composition/Patterns/PatternC05.asm) | #0CF5 | 29 | 5 | 5C |
| [PatternC06](../Source/Music/Composition/Patterns/PatternC06.asm) | #0D12 | 29 | 5 | 6C |
| [PatternC07](../Source/Music/Composition/Patterns/PatternC07.asm) | #0D2F | 15 | 2 | 7C |
| [PatternC08](../Source/Music/Composition/Patterns/PatternC08.asm) | #0D3E | 22 | 3 | 8C |
| [PatternC0D](../Source/Music/Composition/Patterns/PatternC0D.asm) | #0D54 | 106 | 20 | 13C |
| [PatternC0E](../Source/Music/Composition/Patterns/PatternC0E.asm) | #0DBE | 106 | 20 | 14C |
| [PatternC0F](../Source/Music/Composition/Patterns/PatternC0F.asm) | #0E28 | 96 | 19 | 15C |

## Сэмплы

Двенадцать непустых относительных адресов указывают двенадцать непрерывных записей по смещениям 3720..4051. Каждая начинается физическим FMusicLoopHeader, за ним расположены Length экземпляров FMusicSampleStep. Всего 77 четырёхбайтовых шагов. Заголовок задаёт LoopPosition и Length, все значения LoopPosition меньше Length.

FMusicSampleStep содержит ShiftControl, LevelModes и little endian ToneDelta. Схемы разрядов управляющих байтов и действия каждого бита приведены в [MusicSynthesis](MusicSynthesis.md) и в объявлениях STRUCT. Тональная поправка складывается по модулю 65536, поправки шума и огибающей по модулю 256. Имена полей отражают реальное потребление POP DE и POP BC, порядок байтов не изменён.

| Исходник | Смещение | LoopPosition | Length | Байтов |
| --- | --- | ---: | ---: | ---: |
| [Sample01](../Source/Music/Composition/Samples/Sample01.asm) | #0E88 | 11 | 12 | 50 |
| [Sample02](../Source/Music/Composition/Samples/Sample02.asm) | #0EBA | 0 | 1 | 6 |
| [Sample03](../Source/Music/Composition/Samples/Sample03.asm) | #0EC0 | 0 | 1 | 6 |
| [Sample04](../Source/Music/Composition/Samples/Sample04.asm) | #0EC6 | 6 | 7 | 30 |
| [Sample05](../Source/Music/Composition/Samples/Sample05.asm) | #0EE4 | 11 | 12 | 50 |
| [Sample06](../Source/Music/Composition/Samples/Sample06.asm) | #0F16 | 1 | 2 | 10 |
| [Sample07](../Source/Music/Composition/Samples/Sample07.asm) | #0F20 | 0 | 4 | 18 |
| [Sample08](../Source/Music/Composition/Samples/Sample08.asm) | #0F32 | 11 | 12 | 50 |
| [Sample0B](../Source/Music/Composition/Samples/Sample0B.asm) | #0F64 | 6 | 7 | 30 |
| [Sample0C](../Source/Music/Composition/Samples/Sample0C.asm) | #0F82 | 0 | 4 | 18 |
| [Sample0E](../Source/Music/Composition/Samples/Sample0E.asm) | #0F94 | 0 | 6 | 26 |
| [Sample0F](../Source/Music/Composition/Samples/Sample0F.asm) | #0FAE | 8 | 9 | 38 |

## Орнаменты

Четырнадцать записей занимают смещения 4052..4136. После FMusicLoopHeader расположены Length физических FMusicOrnamentStep, всего 57 однобайтовых шагов. Поле NoteDelta является байтовой поправкой индекса ноты. Сложение с текущей нотой оборачивается, затем исходное ядро проверяет старший разряд суммы. Отрицательные байтовые значения не пересчитаны и не ограничены новым алгоритмом.

| Исходник | Смещение | LoopPosition | Length | Байтов |
| --- | --- | ---: | ---: | ---: |
| [Ornament00](../Source/Music/Composition/Ornaments/Ornament00.asm) | #0FD4 | 0 | 1 | 3 |
| [Ornament01](../Source/Music/Composition/Ornaments/Ornament01.asm) | #0FD7 | 0 | 3 | 5 |
| [Ornament02](../Source/Music/Composition/Ornaments/Ornament02.asm) | #0FDC | 0 | 3 | 5 |
| [Ornament03](../Source/Music/Composition/Ornaments/Ornament03.asm) | #0FE1 | 0 | 3 | 5 |
| [Ornament04](../Source/Music/Composition/Ornaments/Ornament04.asm) | #0FE6 | 3 | 4 | 6 |
| [Ornament05](../Source/Music/Composition/Ornaments/Ornament05.asm) | #0FEC | 3 | 4 | 6 |
| [Ornament06](../Source/Music/Composition/Ornaments/Ornament06.asm) | #0FF2 | 3 | 4 | 6 |
| [Ornament07](../Source/Music/Composition/Ornaments/Ornament07.asm) | #0FF8 | 3 | 4 | 6 |
| [Ornament08](../Source/Music/Composition/Ornaments/Ornament08.asm) | #0FFE | 3 | 4 | 6 |
| [Ornament09](../Source/Music/Composition/Ornaments/Ornament09.asm) | #1004 | 3 | 4 | 6 |
| [Ornament0A](../Source/Music/Composition/Ornaments/Ornament0A.asm) | #100A | 0 | 6 | 8 |
| [Ornament0B](../Source/Music/Composition/Ornaments/Ornament0B.asm) | #1012 | 0 | 10 | 12 |
| [Ornament0C](../Source/Music/Composition/Ornaments/Ornament0C.asm) | #101E | 1 | 2 | 4 |
| [Ornament0D](../Source/Music/Composition/Ornaments/Ornament0D.asm) | #1022 | 0 | 5 | 7 |

## Проверка и границы

[MusicCompositionLayout.py](../Tools/Disasm/Research/MusicCompositionLayout.py) проверяет все границы без пересечений и пропусков, размеры заголовков и шагов, ссылки общих потоков и разбор команд с LIFO-параметрами. [Отчёт разметки](../Tools/Disasm/Reports/MusicCompositionLayout.json) содержит каждую физическую область, команду, ссылку и контрольную сумму.

[MusicCompositionSource.py](../Tools/Disasm/Research/MusicCompositionSource.py) строго читает фактические директивы и экземпляры структур, отвергает лишние строки, неправильное число полей и изменение порядка записей. VerifySources сравнивает каждый байт с исходной записью образа, адреса меток и физических полей, размеры и смещения STRUCT. [Отчёт публикации](../Tools/Disasm/Reports/MusicCompositionClassification.json) фиксирует сохранение 4137 байтов и удаление только заменённого бинарного ресурса после проверки, оригинал остаётся в извлечённом MUZ1.C и истории.

CheckFilePlacement проверяет прямую цепочку include и каждый физический диапазон. Нативная сборка не запускалась. Независимые модели исходного проигрывателя совпали на 5377 кадрах, всех 2304 вызовах декодеров, 1793 исполнениях AdvancePatternA и 5377 фазах B/C до первого повтора. Это проверка алгоритмов на исходных байтах, она не подменяет сборку новых текстов, аппаратные IRQ или нативное прослушивание.

Назначение Unknown63, выполнение зарезервированных кодов эффектов, аппаратные IRQ и нативный звук остаются непроверенными. Совпадение байтов не объявлено доказательством полной смысловой завершённости всего проекта.
