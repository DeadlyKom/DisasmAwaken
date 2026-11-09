# Дисковая копия блока полётного состояния

Все 7 213 байтов DATAS.C побайтно совпадают с ACTION.C по
файловым смещениям #2C00..#482C, которым в полёте соответствуют
адреса #8C00..#A82C. Последние 211 байтов выделенных секторов
сохранены отдельно. Исходные копии в двух файлах не объединяются.

Совпадение проверяет [модель](../Tools/Disasm/Research/CheckDatasMirror.py).
Путь загрузки отдельного DATAS пока не установлен. Известные
потребители и писатели областей ACTION описаны в связанных исходниках.
Неизвестные поля и промежутки исходного ACTION остаются неизвестными
и для этой дисковой копии. Назначение DATAS как механизма сброса
состояния этой проверкой не устанавливается.

Начальные #0200 байтов также совпадают с D3D. Для них установлены буквальные чтения обоих краёв широкого пролёта. [Пары ACTION и 3DPART](ActionPolygonExtraMaskPairs.md)

| Смещение DATAS | Длина | Вид ACTION | Соответствующий исходник |
| --- | --- | --- | --- |
| #0000 | 3072 | unclassified | [Source/Resources/17_ACTION/Unclassified020_Prefix.bin](../Source/Resources/17_ACTION/Unclassified020_Prefix.bin) |
| #0C00 | 256 | typed_data | [Source/Action/Data/ProjectionSquares.asm](../Source/Action/Data/ProjectionSquares.asm) |
| #0D00 | 256 | typed_data | [Source/Action/Data/SineTable.asm](../Source/Action/Data/SineTable.asm) |
| #0E00 | 256 | typed_data | [Source/Action/Data/SignedRatioCodes.asm](../Source/Action/Data/SignedRatioCodes.asm) |
| #0F00 | 18 | unclassified | [Source/Resources/17_ACTION/Unclassified020_AfterRatioCodes.bin](../Source/Resources/17_ACTION/Unclassified020_AfterRatioCodes.bin) |
| #0F12 | 3 | typed_data | [Source/Action/Data/RenderPhases.asm](../Source/Action/Data/RenderPhases.asm) |
| #0F15 | 4 | typed_data | [Source/Action/Data/WordRandomState.asm](../Source/Action/Data/WordRandomState.asm) |
| #0F19 | 2 | typed_data | [Source/Action/Data/AimPoint.asm](../Source/Action/Data/AimPoint.asm) |
| #0F1B | 3 | typed_data | [Source/Action/Data/MissileTargets.asm](../Source/Action/Data/MissileTargets.asm) |
| #0F1E | 9 | typed_data | [Source/Action/Data/ComponentWork.asm](../Source/Action/Data/ComponentWork.asm) |
| #0F27 | 72 | typed_data | [Source/Action/Data/WideVectors.asm](../Source/Action/Data/WideVectors.asm) |
| #0F6F | 9 | typed_data | [Source/Action/Data/TransformWorkVector24.asm](../Source/Action/Data/TransformWorkVector24.asm) |
| #0F78 | 9 | typed_data | [Source/Action/Data/WorkVector24.asm](../Source/Action/Data/WorkVector24.asm) |
| #0F81 | 12 | typed_data | [Source/Action/Data/GlyphIndicatorState.asm](../Source/Action/Data/GlyphIndicatorState.asm) |
| #0F8D | 131 | unclassified | [Source/Resources/17_ACTION/Unclassified020_BeforePreferredByte.bin](../Source/Resources/17_ACTION/Unclassified020_BeforePreferredByte.bin) |
| #1010 | 2 | typed_data | [Source/Action/Data/PreferredByteState.asm](../Source/Action/Data/PreferredByteState.asm) |
| #1012 | 2 | typed_data | [Source/Action/Data/MissileStock.asm](../Source/Action/Data/MissileStock.asm) |
| #1014 | 312 | unclassified | [Source/Resources/17_ACTION/Unclassified020_AfterMissileStock.bin](../Source/Resources/17_ACTION/Unclassified020_AfterMissileStock.bin) |
| #114C | 54 | typed_data | [Source/Action/Data/KeyScanInputs.asm](../Source/Action/Data/KeyScanInputs.asm) |
| #1182 | 126 | unclassified | [Source/Resources/17_ACTION/Unclassified020_BeforeObjectPointers.bin](../Source/Resources/17_ACTION/Unclassified020_BeforeObjectPointers.bin) |
| #1200 | 256 | typed_data | [Source/Action/Data/ObjectPointers.asm](../Source/Action/Data/ObjectPointers.asm) |
| #1300 | 512 | unclassified | [Source/Resources/17_ACTION/Unclassified020_AfterObjectPointers.bin](../Source/Resources/17_ACTION/Unclassified020_AfterObjectPointers.bin) |
| #1500 | 1664 | typed_data | [Source/Action/Data/ObjectRecords.asm](../Source/Action/Data/ObjectRecords.asm) |
| #1B80 | 21 | unclassified | [Source/Resources/17_ACTION/Unclassified020_BeforeVisualEffects.bin](../Source/Resources/17_ACTION/Unclassified020_BeforeVisualEffects.bin) |
| #1B95 | 152 | typed_data | [Source/Action/Data/VisualEffects.asm](../Source/Action/Data/VisualEffects.asm) |
