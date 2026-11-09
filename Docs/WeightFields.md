# Кодированные количества оснащения и вторичный индекс

[SumSecondaryIndex](../Source/Text/SumSecondaryIndex.asm) суммирует
SecondaryEquipmentState.Row по 73D8 и младший байт TopRow по 737D.
Результат восьмибитный, A=C, B=0. HL и DE сохраняются, F от ADD,
перенос не расширяет индекс. Эти два операнда использует
[второй список оснащения](SecondaryEquipmentRows.md).

[ReadEquipmentQuantity](../Source/Text/ReadEquipmentQuantity.asm) использует GetEquipIndex и базу EquipmentQuantityCodes по 988E. [ReadSecondQuantity](../Source/Text/ReadSecondQuantity.asm) использует SumSecondaryIndex и базу SecondaryEquipmentData.Quantities по 98F6. Оба передают управление ParseFieldSuffix с двумя допустимыми свойствами s и n. Без точки полный индекс HL прибавляется к базе, читается байт, при установленном бите 7 выполняется CPL. Те же байты читают печататели списков и расчёт нагрузки. [Первый набор](PlayerSavedFields.md), [второй набор](StationTransportTradeTables.md).

Декодированное количество равно исходному байту при значениях 00..7F, иначе байту XOR FF. DE содержит результат с нулевым D. F при снятом бите 7 относится к OR A, при инверсии CPL сохраняет S/Z/PV от исходного OR, устанавливает H/N и берёт X/Y из нового A. Поэтому исходный FF даёт DE=0 с Z=0, исходный 00 даёт DE=0 с Z=1. У печатателя первичного списка исходный 80 завершает обход, прямой читатель декодирует его в 7F.

Без цифр индекс берётся из исходной суммы, с цифрами равен (число-1) AND FFFF. Прямое чтение не обрезает слово до байта. На выходе HL указывает на прочитанный байт, BC по-прежнему содержит исходный байтовый индекс. Общий ReadAtBase первого входа принимает произвольную DE базу и полный HL индекс. Альтернативный B установлен в 2, остальные альтернативные пары и AF' сохраняются на прямом пути, IX продвинут за число, IY, I и IFF сохранены, SP увеличен на два.

Суффикс s первого набора вызывает [CheckThresholdSet30](../Source/Text/CheckThresholdSet30.asm), второго [CheckThresholdSet14](../Source/Text/CheckThresholdSet14.asm), договоры в [ThresholdSets](ThresholdSets.md). Суффикс n вызывает [HasActiveNeighbor](../Source/Text/HasActiveNeighbor.asm) либо [HasSecondActiveNeighbor](../Source/Text/HasSecondActiveNeighbor.asm), договоры в [ActiveNeighbors](ActiveNeighbors.md). Стековый индекс снимается соответствующим обработчиком. При неизвестном суффиксе FindToken передаёт управление SkipLine без обычного результата.

[CheckWeightFields.py](../Tools/Disasm/Research/CheckWeightFields.py) проверил все 65536 пар компонентов вторичного индекса и 3584 прямых чтения количеств, все 256 кодированных байтов, явный ноль, большие числа и переполнение слова. Сверены результат, полный F прямого пути, HL/BC, IX, SP и альтернативные регистры. Отчёт [WeightFieldsVerification](../Tools/Disasm/Reports/WeightFieldsVerification.json). Суффиксные сканеры проверены собственными моделями, но полный составной путь с суффиксом в этой модели не исполнялся. Сборка, IRQ и нативный игровой запуск не выполнялись.
