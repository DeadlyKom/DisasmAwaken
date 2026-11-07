# Внутренние входы алгоритмов вступления

Адресные метки заменены именами операций из разобранных алгоритмов.
Адреса, инструкции, самомодификация и последовательные продолжения сохранены.
Переименование не доказывает новые варианты выполнения.

| Процедура | Адрес | Имя | Операция |
| --- | --- | --- | --- |
| [InitializeIntro](../Source/Intro/InitializeIntro.asm) | #65B0 | EnterStation | передача перенесённому загрузчику станции |
| [BuildAlternatingTexture](../Source/Intro/BuildAlternatingTexture.asm) | #6645 | BeginRow | начало 256-байтовой строки |
| [BuildAlternatingTexture](../Source/Intro/BuildAlternatingTexture.asm) | #6647 | ConvertPair | деление чётного байта и копирование нечётного |
| [ExpandTextureRows](../Source/Intro/ExpandTextureRows.asm) | #6733 | BeginRow | начало очередной 64-байтовой строки |
| [ExpandTextureRows](../Source/Intro/ExpandTextureRows.asm) | #6737 | AddTextureBias | добавление IXL к очередному байту |
| [ExpandTextureRows](../Source/Intro/ExpandTextureRows.asm) | #6747 | RepeatRow | повторение образца до длины страницы |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #6784 | NextParameter | чтение следующего из 63 параметров |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #67A4 | Accumulate | накопление 128 координат с шагом DE |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #67B4 | StoreLookup | адресация и запись пары индекс и IYL |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #67D6 | BeginGapPass | начало одного из двух проходов заполнения |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #67D9 | CheckGap | проверка второго байта очередной пары |
| [BuildTextureLookup](../Source/Intro/BuildTextureLookup.asm) | #67E7 | NextPair | продолжение после исходной либо восстановленной пары |
| [BuildAttributeWriter](../Source/Intro/BuildAttributeWriter.asm) | #6935 | WriterRow | начало одной из восьми строк писателя |
| [BuildAttributeWriter](../Source/Intro/BuildAttributeWriter.asm) | #6939 | WriterWord | генерация POP HL и LD (nn),HL |
| [CombineAttributeNibbles](../Source/Intro/CombineAttributeNibbles.asm) | #6967 | AttributeRow | выбор младшей тетрады строки |
| [CombineAttributeNibbles](../Source/Intro/CombineAttributeNibbles.asm) | #6971 | AttributeCell | объединение тетрады строки и тетрады столбца |
| [BuildScreenTables](../Source/Intro/BuildScreenTables.asm) | #69BC | MirrorIndex | отражение исходной половины координат |
| [BuildScreenTables](../Source/Intro/BuildScreenTables.asm) | #69CA | FirstTableRow | два экранных указателя первой таблицы |
| [BuildScreenTables](../Source/Intro/BuildScreenTables.asm) | #69E3 | CountFirstRow | счётчик после коррекции экранного адреса |
| [BuildScreenTables](../Source/Intro/BuildScreenTables.asm) | #69ED | SecondTableRow | указатели второй таблицы со сдвигом H на два |
| [RepeatPattern](../Source/Intro/RepeatPattern.asm) | #6A21 | CopyPattern | перенос очередной копии образца |
| [RunTimedEffect](../Source/Intro/RunTimedEffect.asm) | #6A4E | CheckSpace | проверка Space перед очередным кадром |
| [FillBitmap](../Source/Intro/FillBitmap.asm) | #6A6C | FillScanline | заполнение 32 байтов экранной строки |
| [FillBitmap](../Source/Intro/FillBitmap.asm) | #6ABE | CountScanline | счётчик после расчёта следующей строки |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6ADD | ColumnTable | начало одной из 16 таблиц столбцов |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6AE3 | CheckUpper | проверка верхнего ограничения страницы E8 |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6AE9 | CheckLower | проверка нижнего ограничения страницы D8 |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6AEE | StoreColumn | сохранение допустимой страницы либо нуля |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6B05 | CopyTail | перенос 32-байтового табличного хвоста |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6B28 | TextureRow | начало страницы преобразуемой текстуры |
| [InitializeColumnEffect](../Source/Intro/InitializeColumnEffect.asm) | #6B2A | SumSquare | сумма соседних пикселей квадрата 2 на 2 |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6CDA | WriterRow | начало одной из 38 строк писателя |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6CDC | WriterWord | генерация очередного четырёхбайтового звена |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6CF9 | BuildNibble | выделение старшей тетрады индекса |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D24 | PointerRow | начало строки из 16 указателей |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D27 | CheckUpper | проверка верхней границы 80 |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D2E | CheckLower | проверка нижней границы 70 |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D34 | StorePage | преобразование ограниченного значения в страницу |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D49 | CountPtrRow | счётчик строк после изменения стартовой страницы |
| [InitializeLookupEffect](../Source/Intro/InitializeLookupEffect.asm) | #6D4F | WarmPhases | одно из 40 подготовительных обновлений фаз |
| [BuildIntroTexture](../Source/Intro/BuildIntroTexture.asm) | #6D9A | CopySampleRow | перенос 128 байтов из середины страницы |
| [BuildMirroredTexture](../Source/Intro/BuildMirroredTexture.asm) | #6DF0 | MirrorRow | подготовка и копирование очередных 32 байтов |
| [BuildMirroredTexture](../Source/Intro/BuildMirroredTexture.asm) | #6DFE | MirrorPixel | нормализация и отражение очередного байта строки |
| [BuildMirroredTexture](../Source/Intro/BuildMirroredTexture.asm) | #6E15 | MirrorHalf | обратное копирование первой половины во вторую |

Проверка положения всех кодовых меток выполняется
[CheckSourceLabels](../Tools/Disasm/Research/CheckSourceLabels.py),
инструкции сравнивает [VerifySources](../Tools/Disasm/VerifySources.py).
