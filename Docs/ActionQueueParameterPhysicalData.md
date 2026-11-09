# Рабочие поля очереди, отсечения и набора параметров

Оформлены 18 существующих байтов общего ядра ACTION в фиксированном банке 2. Физический файл ACTION содержит их по смещениям 3BA1..3BB2, CPU читает их по 9BA1..9BB2. Новая память не выделяется. Соседние неизвестные байты сохранены отдельно.

| Адрес | Физическая запись | Тип и размер |
|---|---|---|
| 9BA1..9BA2 | [RenderQueueCursor](../Source/Action/Data/RenderQueueCursor.asm) | FRenderQueueCursor, 2 байта |
| 9BA3 | [ClipOutputState](../Source/Action/Data/ClipOutputState.asm) | FClipOutputState, 1 байт |
| 9BA4..9BB2 | [ParameterSet](../Source/Action/Data/ParameterSet.asm) | FActionParameterSet, 15 байтов |

## Очередь и результат отсечения

Head по смещению 0 содержит младшую часть адреса узла страницы 8F. Рабочий признак конца цепочки равен 01. FreeOffset по смещению 1 задаёт место следующего узла, увеличивается на 0E, значение FC запрещает вставку. [InsertRenderQueue](../Source/Action/InsertRenderQueue.asm) изменяет поля при вставке, [ReadRenderQueue](../Source/Action/ReadRenderQueue.asm) использует Head для обхода. [RenderSceneFrame](../Source/Action/RenderSceneFrame.asm) записывает слово 0001 по адресу Head, одновременно задавая Head=01 и FreeOffset=00. Сортировка и восстановление снимка описаны в [разборе вставки](ActionRenderQueueInsert.md) и [чтения](ActionRenderQueueControl.md).

OutputSize содержит длину в байтах, а не число вершин. [ClipPolygon](../Source/Action/ClipPolygon.asm) обнуляет её перед обходом, писатели [пересечений](ActionClipIntersections.md) добавляют пары Second, First в страницу 90 и увеличивают длину на два с байтовым оборачиванием. Произвольная длина не является доказательством допустимого игрового контура.

Все три исходных байта равны нулю. Начальный Head=00 не заменён на рабочий маркер 01. Назначение поля установлено по обращениям процедур, нулевой инициализатор не объявляется корректной пустой очередью.

## Пятнадцать полей параметров

Физический порядок полей FActionParameterSet совпадает с чтением [ApplyParameterSet](../Source/Action/ApplyParameterSet.asm). Таблица адресов и локальных назначений приведена в [описании применения](ActionApplyParameters.md). Имя каждого поля обозначает доказанный изменяемый операнд либо его установленную роль. Поле ReadOnly01 читается без записи именно этой процедурой, это не объявление отсутствия других потребителей. CompareAdd06 используется дважды, в CP по 7B6A и ADD A,n по 6873.

[BuildParameterTables](../Source/Controls/BuildParameterTables.asm) вычисляет все 15 байтов по зерну, потоку генератора, коэффициентам и шаблонам. Физические исходные значения всех полей равны нулю. Они не тождественны исходным операндам потребителей. Например, Link1ABaseLimit и OtherLinkLimit в исходных инструкциях равны 0A, а не нулю. Значение параметра переносится в операнд только после выполнения ApplyParameterSet. Полный игровой смысл всех параметров остаётся неизвестным.

## Проверка

[Описание физических полей](../Tools/Disasm/Research/ActionQueueParameterPhysicalData.py) и [отчёт](../Tools/Disasm/Reports/ActionQueueParameterPhysicalDataClassification.json) связывают размещение, размеры и инициализаторы с исходным дисковым файлом. Существующие числовые имена Head, FreeOffset, OutputSize и Parameters дополнены ASSERT на физические поля.

Проверки очереди, пересечений, генератора и применения перечислены в REQUIRED_REPORTS исследовательского описания. [Отдельная модель порогов](../Tools/Disasm/Reports/ActionMutableEffectLimitsVerification.json) исполняет настоящий писатель и потребитель до развилки в 136192 сценариях, тело эффекта в ней не выполняется. Проверка физических записей не запускает сборку и не доказывает нативную работу игры.
