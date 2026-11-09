# Физические управления полётом и зерно параметров

Две записи находятся в исходном общем ядре ACTION, их адреса и восемь дисковых байтов не изменены. STRUCT описывает реальные поля, экземпляры входят в [17_ACTION.inc](../Source/Files/17_ACTION.inc). Соседние байты остаются отдельными неизвестными диапазонами.

## Управления точками

[ActionFlightControls.Value](../Source/Action/Data/FlightControls.asm) имеет тип FFlightControls и занимает 9B95..9B97.

| Смещение | Поле | Исходный байт | Потребитель |
|---|---|---|---|
| 0 | YControl | 00 | Знаковое управление первым проходом коррекции Y |
| 1 | XControl | 00 | Знаковое управление вторым проходом коррекции X |
| 2 | TurnControl | 00 | Отрицание по модулю 256 задаёт индекс синусоиды табличного преобразования |

Это числовые signed8, а не независимые флаги. Код 00 означает отсутствие соответствующего смещения либо пропуск преобразования, FF означает -1, 80 означает -128. Значения и ограничения реальных клавиатурных писателей не следует заменять этим полным диапазоном представления.

[UpdateBufferPoints](../Source/Controls/UpdateBufferPoints.asm) читает эти поля при последовательной обработке 35 физических FBufferPoint. Порядок Y, X, преобразование и исходные единичные поправки описаны в [ControlsPointMotion](ControlsPointMotion.md). [LatchControlsAndDecay](../Source/Action/LatchControlsAndDecay.asm) приближает ненулевые значения к нулю только при разрешении старого запрета и циклической фазы. [Описание затухания](ActionControlDecay.md) отдельно учитывает задержку запроса на один вызов.

Шесть клавиатурных писателей сохраняют свои исходные ограничения и накопители повторов, [RequestYNegative](../Source/Action/RequestYNegative.asm), [RequestYPositive](../Source/Action/RequestYPositive.asm), [RequestXNegative](../Source/Action/RequestXNegative.asm), [RequestXPositive](../Source/Action/RequestXPositive.asm), [RequestTurnNegative](../Source/Action/RequestTurnNegative.asm), [RequestTurnPositive](../Source/Action/RequestTurnPositive.asm). Физическая типизация не меняет алгоритм писателей.

## Зерно генератора

[ActionParameterSeeds.Value](../Source/Action/Data/ParameterSeeds.asm) имеет тип FParameterSeeds и занимает 9BC1..9BC5.

| Смещение | Поле | Размер | Исходное значение |
|---|---|---|---|
| 0 | SeedFirst | 2 | 4B38, младший байт 38 |
| 2 | SeedSecond | 2 | 4AF4, младший байт F4 |
| 4 | StepControl | 1 | 00 |

[BuildParameterTables](../Source/Controls/BuildParameterTables.asm) читает оба слова и полный StepControl. По этим данным строятся пятнадцать параметров и девять строковых значений. Математика свёртки, повторов генератора, групп шаблонов и коэффициентов находится в [ControlsParameterTables](ControlsParameterTables.md). Новый экземпляр не добавляет память и не заменяет вычисленный буфер Parameters исходными значениями.

Те же физические байты имеют других читателей. [CompareContextWordPairs](../Source/Action/CompareContextWordPairs.asm) сравнивает два слова с соседней парой. [SpawnAlternate](../Source/Action/SpawnAlternate.asm) читает пять байтов существующего контекста. Это не доказательство нового самостоятельного сохранения либо полного игрового значения всех связанных полей, эти роли не переименованы по предположению.

## Привязки и проверка

Существующие имена ControlsPointMotionState и ControlsParameterTablesState оставлены. В [переменных](../Includes/Variables/Include.inc) добавлены ASSERT, связывающие шесть числовых адресов с полями физических экземпляров. Формат числовых EQU сохранён для действующего статического анализатора.

[Описание и обратимый разбор записей](../Tools/Disasm/Research/ActionInputContextData.py), [публикация](../Tools/Disasm/Research/ClassifyActionInputContextData.py), [отчёт](../Tools/Disasm/Reports/ActionInputContextDataClassification.json). VerifySources читает реальные STRUCT, поля и инициализаторы, сопоставляет их с восемью исходными байтами и зарегистрированными символами. Все исходные инструкции проверяются отдельно и не изменены. Сборка и нативное исполнение новой разметки не выполнялись.
