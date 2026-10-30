# Добавление значений в стек выражений

CPU-стек хранит возвраты процедур. Отдельный стек выражений задаётся альтернативным HL, указывающим на два следующих доступных байта. Новых областей эти функции не выделяют.

[ReadCredits](../Source/Text/ReadCredits.asm) читает слово #984E в DE и последовательно входит в [PushExpressionWord](../Source/Text/PushExpressionWord.asm). Последний переносит DE в альтернативный набор через CPU-стек, записывает младший и старший байты, увеличивает альтернативный HL на два. Основные HL/BC/AF сохраняются, основной DE и альтернативный DE содержат прочитанное слово. Жёсткий порядок этих двух include обязателен.

[ReadFieldLowerj](../Source/Text/ReadFieldLowerj.asm) читает байт #9850 и имеет общий AppendByte. Вход получает байт в A, переключается EXX, записывает A и нулевой старший байт, увеличивает альтернативный HL на два и возвращает основной набор. В отличие от словного PushExpressionWord альтернативный DE не изменяется. Основные HL/DE/BC и F сохраняются.

Байтовые входы:

- [ReadFieldUpperJ](../Source/Text/ReadFieldUpperJ.asm), исходный байт #9851.
- [PushTrue](../Source/Text/PushTrue.asm), логическая единица, F сохранён.
- [PushFalse](../Source/Text/PushFalse.asm), ноль, F=44 от XOR A.
- [ReadEventCode](../Source/Text/ReadEventCode.asm), код события #983A.
- [ReadFieldLoweru](../Source/Text/ReadFieldLoweru.asm), байт #984B.

Игровые единицы неизвестных скалярных полей не выводятся из ширины их чтения. Все байтовые записи создают слово со старшим нулём. SP после обычного RET увеличен на два, альтернативные BC/AF, индексные регистры, I и IFF сохраняются.

Следующие обёртки состоят строго из CALL установленного читателя и JP PushExpressionWord. Их основные регистры и флаги равны выходу читателя, DE дополнительно записывается в стек выражений. Альтернативный HL продвигается на два, альтернативный DE получает результат, остальные эффекты сохраняются по договору читателя. Если читатель переходит в SkipLine без возврата, запись не достигается.

- [ReadFieldLowero](../Source/Text/ReadFieldLowero.asm) вызывает [ReadEquipmentWeight](../Source/Text/ReadEquipmentWeight.asm).
- [ReadFieldLoweri](../Source/Text/ReadFieldLoweri.asm) вызывает [ReadSecondWeight](../Source/Text/ReadSecondWeight.asm).
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

Композиция обёрток подтверждается статическим сравнением их точных двух инструкций и отдельными моделями установленных читателей. Полного составного прогона всех обёрток здесь не выполнялось.

[CheckExpressionPushes.py](../Tools/Disasm/Research/CheckExpressionPushes.py) исполняет байтовые загрузчики, общий AppendByte, логические константы и словный последовательный вход в 328192 байтовых и 65536 словных случаях. Проверяются все значения байта и F, все значения слова с варьированием F, запись двух байтов, сохранность основных и альтернативных регистров, отличие DE альтернативного набора и SP. Отчёт [ExpressionPushesVerification](../Tools/Disasm/Reports/ExpressionPushesVerification.json). Прерывания, сборка и нативный запуск не выполнялись.
