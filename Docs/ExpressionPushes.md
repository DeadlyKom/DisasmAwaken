# Добавление значений в стек выражений

CPU-стек хранит возвраты процедур. Отдельный стек выражений задаётся альтернативным HL, указывающим на два следующих доступных байта. Новых областей эти функции не выделяют.

[ReadCredits](../Source/Text/ReadCredits.asm) читает слово #984E в DE и последовательно входит в [PushExpressionWord](../Source/Text/PushExpressionWord.asm). Последний переносит DE в альтернативный набор через CPU-стек, записывает младший и старший байты, увеличивает альтернативный HL на два. Основные HL/BC/AF сохраняются, основной DE и альтернативный DE содержат прочитанное слово. Жёсткий порядок этих двух include обязателен.

[PushUsedTonnage](../Source/Text/PushUsedTonnage.asm) читает байт #9850 и имеет общий AppendByte. Вход получает байт в A, переключается EXX, записывает A и нулевой старший байт, увеличивает альтернативный HL на два и возвращает основной набор. В отличие от словного PushExpressionWord альтернативный DE не изменяется. Основные HL/DE/BC и F сохраняются.

Байтовые входы:

- [PushTonnageCapacity](../Source/Text/PushTonnageCapacity.asm), исходный байт #9851.
- [PushTrue](../Source/Text/PushTrue.asm), логическая единица, F сохранён.
- [PushFalse](../Source/Text/PushFalse.asm), ноль, F=44 от XOR A.
- [ReadEventCode](../Source/Text/ReadEventCode.asm), код события #983A.
- [ReadFieldLoweru](../Source/Text/ReadFieldLoweru.asm), байт #984B.

Игровые единицы неизвестных скалярных полей не выводятся из ширины их чтения. Все байтовые записи создают слово со старшим нулём. SP после обычного RET увеличен на два, альтернативные BC/AF, индексные регистры, I и IFF сохраняются.

Следующие обёртки состоят строго из CALL установленного читателя и JP PushExpressionWord. Их основные регистры и флаги равны выходу читателя, DE дополнительно записывается в стек выражений. Альтернативный HL продвигается на два, альтернативный DE получает результат, остальные эффекты сохраняются по договору читателя. Если читатель переходит в SkipLine без возврата, запись не достигается.

- [ReadFieldLowero](../Source/Text/ReadFieldLowero.asm) вызывает [ReadEquipmentQuantity](../Source/Text/ReadEquipmentQuantity.asm).
- [ReadFieldLoweri](../Source/Text/ReadFieldLoweri.asm) вызывает [ReadSecondQuantity](../Source/Text/ReadSecondQuantity.asm).
- [ReadFieldLowerk](../Source/Text/ReadFieldLowerk.asm) вызывает [ReadSelectedPrimaryFields](../Source/Text/ReadSelectedPrimaryFields.asm).
- [ReadFieldLowerr](../Source/Text/ReadFieldLowerr.asm) вызывает [ReadSelectedSecondaryFields](../Source/Text/ReadSelectedSecondaryFields.asm).
- [ReadFieldUpperG](../Source/Text/ReadFieldUpperG.asm) вызывает [ReadMarketField](../Source/Text/ReadMarketField.asm).
- [ReadFieldUpperO](../Source/Text/ReadFieldUpperO.asm) вызывает [CheckEquipmentThreshold](../Source/Text/CheckEquipmentThreshold.asm).
- [ReadFieldUpperI](../Source/Text/ReadFieldUpperI.asm) вызывает [CheckSecondEntryThreshold](../Source/Text/CheckSecondEntryThreshold.asm).
- [ReadFieldUpperK](../Source/Text/ReadFieldUpperK.asm) вызывает [ReadBank4PrimaryFields](../Source/Text/ReadBank4PrimaryFields.asm).
- [ReadFieldUpperR](../Source/Text/ReadFieldUpperR.asm) вызывает [ReadBank4SecondaryFields](../Source/Text/ReadBank4SecondaryFields.asm).
- [ReadFieldLowerg](../Source/Text/ReadFieldLowerg.asm) вызывает [ReadCargoField](../Source/Text/ReadCargoField.asm).
- [ReadFieldUpperL](../Source/Text/ReadFieldUpperL.asm) вызывает [ReadCurrentKeyParams](../Source/Text/ReadCurrentKeyParams.asm).
- [ReadFieldLowerl](../Source/Text/ReadFieldLowerl.asm) вызывает [ReadOtherKeyParams](../Source/Text/ReadOtherKeyParams.asm).
- [ReadFieldUpperY](../Source/Text/ReadFieldUpperY.asm) вызывает [ReadCurrentKeyCodes](../Source/Text/ReadCurrentKeyCodes.asm).
- [ReadFieldLowery](../Source/Text/ReadFieldLowery.asm) вызывает [ReadOtherKeyCodes](../Source/Text/ReadOtherKeyCodes.asm).

Композиция обёрток подтверждается статическим сравнением их точных двух инструкций и отдельными моделями установленных читателей. Полного составного прогона всех обёрток здесь не выполнялось. Четыре композиции селекторов записей, четыре композиции параметров ключа и прямые пути двух читателей количества, а также рынок и груз дополнительно исполнены полностью, их области описаны ниже.

[CheckExpressionPushes.py](../Tools/Disasm/Research/CheckExpressionPushes.py) исполняет байтовые загрузчики, общий AppendByte, логические константы и словный последовательный вход в 328192 байтовых и 65536 словных случаях. Проверяются все значения байта и F, все значения слова с варьированием F, запись двух байтов, сохранность основных и альтернативных регистров, отличие DE альтернативного набора и SP. Отчёт [ExpressionPushesVerification](../Tools/Disasm/Reports/ExpressionPushesVerification.json). Прерывания, сборка и нативный запуск не выполнялись.

## RAM и R простых загрузчиков

Общий AppendByte и байтовые входы записывают только два байта выражения, A и нулевой старший байт, CPU-стек не записывают. DE' сохраняется, это отличается от словного PushExpressionWord. ReadCredits читает Money и последовательно входит в словный помощник, который дополнительно временно записывает DE в два байта ниже входного SP. Слово возврата во всех случаях сохраняется, POP не очищает временную RAM.

AppendByte выполняет 7 M1, PushUsedTonnage 8, остальные байтовые входы PushTonnageCapacity, PushTrue, PushFalse, ReadEventCode и ReadFieldLoweru выполняют 9. ReadCredits выполняет 11 M1, включая ED-префикс чтения DE. Младшие семь битов R увеличиваются по модулю 128, старший сохраняется. Сохранение F у байтовых входов не означает сохранения R.

Расширенная CheckExpressionPushes проверяет точный R и все собственные записи CPU в 328192 байтовых и 65536 словных случаях. Сверены физические байты LANG с оригинальным TRD, наблюдатель подтверждён реальной инструкцией записи CPU. Произвольные адреса стеков, полное произведение входных регистров и шинный порядок PUSH не проверяются. Прерывания, сборка и нативный запуск не выполнялись.


## Полные композиции четырёх селекторов записей

[CheckRecordFieldSelectors.py](../Tools/Disasm/Research/CheckRecordFieldSelectors.py) с аргументом --expression-wrappers исполняет ReadFieldLowerk, ReadFieldLowerr, ReadFieldUpperK и ReadFieldUpperR. Выполняются настоящие CALL читателя, ParseFieldSuffix, поиск поля, пятибайтовое чтение, банковый сумматор при необходимости, JP PushExpressionWord и возврат вызывающему. Дочерние процедуры не подменяются.

Все 28672 случая прежней выборки селекторов повторены через эти четыре обёртки. Сверены обычный выход читателя, запись результата по B800..B801, увеличение HL' до B802 и перенос результата в DE'. Без суффикса выбранные читатели записывают исходный байт выбора, банковые константу 127, явное число само по себе не заменяет этот результат.

При исходном SP=7FFE собственный CALL обёртки использует пару 7FFC..7FFD. После возврата читателя PUSH DE словного писателя записывает результат в эту же пару. Исходный возврат по 7FFE..7FFF сохраняется. Все остальные стековые записи всей проверенной цепочки лежат в 7FF4..7FFD. Вне стека проверена точная последовательность CurrentPage при банковом читателе, DefaultTarget парсера и двух байтов выражения, других записей нет.

[Отчёт полного прогона](../Tools/Disasm/Reports/RecordFieldExpressionWrappersVerification.json) отделён от [прямых входов](../Tools/Disasm/Reports/RecordFieldSelectorsVerification.json). В обоих режимах повторно прошли по 28672 случая, проверены физические хеши и наблюдатель CPU. Полный R цепочки, все размещения указателей и стека, страницы, ошибочные суффиксы и оставшиеся обёртки не объявляются доказанными этим прогоном. IRQ, сборка и нативный запуск не выполнялись.


## Полные композиции параметров ключа

[CheckKeyFieldSelectors.py](../Tools/Disasm/Research/CheckKeyFieldSelectors.py) с аргументом --expression-wrappers исполняет ReadFieldUpperL, ReadFieldLowerl, ReadFieldUpperY и прямой вход ReadFieldLowery. Во всех 10920 обычных случаях выполняются настоящий разбор, поиск, запрос характеристики через банковые обёртки при наличии свойства и словный писатель выражения. Выходные основные регистры сохраняют результат соответствующего селектора, HL' увеличивается до B802, DE' получает записанное слово.

Без точки запись выражения содержит CA25 либо CA2E, якорь таблицы, а не числовой признак. При исходном SP=7FFE собственный CALL занимает 7FFC..7FFD, последующий PUSH DE писателя повторно записывает эту пару результатом. Возврат по 7FFE..7FFF сохраняется. Остальные временные записи проверенной банковой цепочки ограничены 7FEE..7FFD. Вне стека сверены DefaultTarget, вся последовательность WorkKey и CurrentPage при запросе свойства и два байта выражения.

Дополнительные 5070 случаев покрывают все недопустимые байты суффикса при пяти префиксах. Промах достигает SkipLine со SP=7FF8, SavedSP восстанавливает 7FFE. После пропуска X до CR следующий NUL возвращает управление по исходному возврату с SP=8000. JP PushExpressionWord не достигается, два контрольных байта выражения CC DD и исходный HL'=B800 сохраняются, банковых переключений и записей WorkKey нет.

ReadFieldLowery проверен как прямой физический вход. В обычном DispatchReadField его запись y по C9EC затенена более ранней y по C998, выбирающей PushTrue. Полный прямой прогон не доказывает штатную достижимость затенённого входа.

[Отчёт](../Tools/Disasm/Reports/KeyFieldExpressionWrappersVerification.json) отделён от прямых селекторов. Физические сектора и SHA256 оригинального TRD проверены. Полный R, все слова ключей, все размещения текста и стека, прерывания, сборка и игровой запуск этим прогоном не доказаны.


## Прямые композиции двух читателей количества

[CheckWeightFields.py](../Tools/Disasm/Research/CheckWeightFields.py) с аргументом --expression-wrappers исполняет ReadFieldLowero и ReadFieldLoweri через настоящие ReadEquipmentQuantity, ReadSecondQuantity, необязательный числовой разбор и PushExpressionWord. В 3584 случаях проверены все 256 кодированных байтов при семи вариантах префикса для каждого входа. Суффиксы s и n этим режимом не исполняются.

При входном SP=7FFE собственный CALL обёртки пишет адрес последующего JP в 7FFC..7FFD. Временные рамки дочернего читателя располагаются на два байта ниже соответствующих рамок его отдельного прогона. После возврата словный PUSH DE повторно использует 7FFC..7FFD для декодированного количества и нулевого старшего байта. Исходный возврат по 7FFE..7FFF сохраняется. Сверена вся последовательность записей CPU, включая DefaultTarget и два байта выражения по B800..B801.

Итоговый HL'=B802, DE' равно декодированному количеству. Основные регистры и F сохраняют выход прямого читателя. Исходные FF и 00 дают одинаковое количество 0, но разные Z, словный писатель это различие не исправляет. Полная обёртка добавляет к стоимости дочернего читателя 11 M1, CALL, JP и девять инструкций PushExpressionWord. Точный R проверен по модулю 128 с сохранностью бита 7.

[Отчёт](../Tools/Disasm/Reports/QuantityExpressionWrappersVerification.json) отделён от прямых читателей. В том же запуске повторно прошли 196608 случаев трёх сумматоров индекса. Все адреса стека, полное произведение регистров, суффиксные ветви и аппаратный запуск не объявляются доказанными.


## Полные композиции рынка и груза

[CheckMarketField.py](../Tools/Disasm/Research/CheckMarketField.py) и [CheckCargoField.py](../Tools/Disasm/Research/CheckCargoField.py) с аргументом --expression-wrapper исполняют ReadFieldUpperG и ReadFieldLowerg через настоящие читатели и PushExpressionWord. Пройдено 4480 рыночных случаев, по 1120 для прямого количества, цены c, допуска продажи s и взвешенной суммы m. Для груза пройдено 2240 случаев, по 1120 для полного первого байта и цены приобретения c. Синтетические данные и пределы выбора остаются теми же, что в прямых моделях.

Проверены результат DE, IX, SP, IY, слово по B800..B801, HL'=B802 и DE', равный результату. Снятый возврат CALL читателя по 7FFC..7FFD повторно используется PUSH DE словного писателя. Исходный возврат по 7FFE..7FFF сохраняется. Все остальные зарегистрированные стековые записи лежат в 7FF4..7FFD.

Нестековая последовательность начинается с DefaultTarget. Для рыночного m затем сверены два байта SelectedRow и все 30+14 записей множителей по C8BF и C8E1, независимо рассчитанные own_writes. После обычного результата записывается слово выражения. Других нестековых записей в проверенных случаях нет. Суффиксные обработчики и взвешенное ядро не подменялись.

[Рыночный отчёт](../Tools/Disasm/Reports/MarketFieldExpressionWrapperVerification.json) и [грузовой отчёт](../Tools/Disasm/Reports/CargoFieldExpressionWrapperVerification.json) отделены от прямых входов. Проверены физический TRD, секторные хеши и наблюдатель CPU. Полные флаги каждого дочернего пути, полный R, все адреса, ошибочные суффиксы и игровой запуск этими составными моделями не доказаны. Смысл bit7 QuantityAndMark остаётся открытым.


## Прямые композиции двух пороговых читателей

[CheckEntryThreshold.py](../Tools/Disasm/Research/CheckEntryThreshold.py) с аргументом --expression-wrappers исполняет ReadFieldUpperO и ReadFieldUpperI через настоящие CheckEquipmentThreshold и CheckSecondEntryThreshold. Пройдены 848 случаев с необязательными числами, всеми байтами порога и четырьмя вариантами текущего ключа. Суффиксные пути c, v, s и k не исполняются этим режимом.

Результат DE=0 либо 1 записывается словом по B800..B801, HL'=B802 и DE' равно записанному результату. Основные выходные регистры и полные флаги читателя сверены, успешный F=0 и F отказа остаются различными. Собственный CALL обёртки и PUSH DE словного писателя повторно используют 7FFC..7FFD при исходном SP=7FFE. Возврат по 7FFE..7FFF сохраняется.

Все прочие временные записи проверенной цепочки находятся в 7FEC..7FFD. Вне стека сверены DefaultTarget, WorkKey, CurrentPage и два байта выражения. Полная независимая последовательность банкового ядра и границы выборки описаны в [EntryThreshold](EntryThreshold.md#нестековые-записи-прямого-пути). [Отчёт](../Tools/Disasm/Reports/EntryThresholdExpressionWrappersVerification.json) отделён от прямых входов. Полный R, все ключи и суффиксы, IRQ, сборка и нативный запуск не доказаны.


Четыре допустимых суффикса двух пороговых обёрток дополнительно проверены полным исполнением в 10400 случаях. Их B, A и F определяются выбранным читателем, а банковый запрос прямого порога не исполняется. Составной писатель сохраняет эти основные выходы. [Подробности и отдельные отчёты](EntryThreshold.md#полные-суффиксные-пути-и-оставшийся-b).


Суффиксы s и n ReadFieldLowero и ReadFieldLoweri дополнительно проверены отдельной полной моделью, 5200 составных случаев. В отличие от прямого чтения, результаты BC и F определяются обработчиком набора либо соседей, s записывает Limit и банковое состояние. [Описание, пределы и отчёты](WeightFields.md#полные-суффиксы-s-и-n).
