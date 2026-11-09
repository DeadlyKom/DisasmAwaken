# Физические ячейки проекции ACTION

[ProjectedPoints.asm](../Source/Action/Data/ProjectedPoints.asm) содержит 40 физических экземпляров существующей FRenderProjectedPoint, Point00..Point27. Они занимают 200 исходных байтов 8E00..8EC7 общего ядра ACTION. В [17_ACTION.inc](../Source/Files/17_ACTION.inc) сохранён исходный физический порядок. Новая память не выделяется.

| Смещение | Поле | Размер | Когда получает runtime-значение |
|---|---|---|---|
| 0 | Second | 2 | ProjectRenderVertex записывает второе экранное слово |
| 2 | First | 2 | ProjectRenderVertex записывает первое экранное слово |
| 4 | ClipCode | 1 | ClassifyProjectedVertices записывает парные признаки положения, сама перспектива этот байт сохраняет |

Значения инициализаторов являются точными дисковыми байтами прежней рабочей RAM. Это не готовая модель и не заранее вычисленные координаты текущего объекта. Маркеры отказа перспективы, в частности старший байт Second=80, имеют отдельный смысл и не исправляются типизацией.

## Производители и последовательность

[TransformObjectVertices](../Source/Action/TransformObjectVertices.asm) перед проходом устанавливает NextOffset=4. [ProjectRenderVertexGroup](../Source/Action/ProjectRenderVertexGroup.asm) получает рабочий SP=8E00+NextOffset. [ProjectRenderVertex](../Source/Action/ProjectRenderVertex.asm) записывает слова двумя PUSH в SP-4..SP-1. Затем рабочий SP увеличивается на пять, поэтому первая запись начинается именно по 8E00, а пятый байт не заполняется перспективой.

[ClassifyProjectedVertices](../Source/Action/ClassifyProjectedVertices.asm) впоследствии читает слова и записывает ClipCode. При раннем маркере последующие коды сохраняются. Поэтому физический ненулевой либо нулевой инициализатор ClipCode не следует считать кодом уже обработанной точки. [Схема разрядов 7..0, девять допустимых кодов и смысл нуля](ActionVertexCodes.md) описаны отдельно.

## Почему оформлены 40 записей

[Проверка всего прохода вершин](../Tools/Disasm/Research/CheckActionObjectVertices.py) проверила все 128 исходных чётных указателей OBJECT3D с разными базами и матрицами. Максимум исходных потоков составляет 40 точек, конечный NextOffset не больше CC. [Отчёт](../Tools/Disasm/Reports/ActionObjectVerticesVerification.json) подтверждает реальные дочерние вызовы, восемь физических банков, регистры кроме R, всю RAM и кратность записей.

Число 40 является пределом этих исходных моделей. Код генератора не проверяет
ёмкость, локальная проверка классификатора покрывает количества 1..50.
Хвост 8EC8..8EFF сохранён как [неразобранные байты](../Source/Resources/17_ACTION/Unclassified2EC8_2F00.bin).
Страницы 8F и 90 описаны в [рабочих областях](ActionInitialStorage.md).
При переходе страницы сохраняется только младший NextOffset.

[Описание записей и обратимый разбор](../Tools/Disasm/Research/ActionProjectedPointsData.py), [публикация](../Tools/Disasm/Research/ClassifyActionProjectedPointsData.py), [отчёт физической типизации](../Tools/Disasm/Reports/ActionProjectedPointsDataClassification.json). VerifySources сверяет каждый инициализатор с оригиналом, размеры и смещения существующей STRUCT, 160 физических имён и начало WorkPage. Генерируемые во время игры значения в TRD не подставляются. Сборка и нативный запуск новой разметки не выполнялись.
