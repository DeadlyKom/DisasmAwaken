# Инициализируемые обёртки рисования

В таблице FInterfaceItem обнаружена 21 шестибайтовая обёртка вида
LD HL,nn и JP DrawCenteredItem. Они относятся к DrawItem02..09, 14..18,
21, 28..30, 33, 35..37. Номер имени соответствует записи интерфейса,
но непосредственное слово в исходном дисковом коде равно нулю.

## Фактическая инициализация

Исходный участок загрузчика #4257..#4275 перебирает таблицу #F0FD до
первого X=#80. C начинается с нуля, DE=#10 задаёт шаг записи.
Из смещений +12,+13 берётся DrawHandler. По DrawHandler+1 записывается C,
по DrawHandler+2 ноль. Затем C увеличивается, IX продвигается к следующей записи.

Этот цикл заполняет 46 обработчиков. Он изменяет операнд LD HL,nn,
а не поле +5 структуры FInterfaceItem. Поле +5 используется как TextIndex
в общих рисователях, его значения сохраняются во время инициализации.

Адреса 21 установленных операндов названы DrawItemState.IndexNN
в Includes/Variables/Include.inc. Это привязки к существующим байтам кода,
не новые переменные и не выделенная память.

## Договор обёртки

В активном состоянии HL на входе игнорируется. Первое действие загружает индекс из изменяемого
операнда. Вторая инструкция передаёт управление хвостовым JP,
дополнительного адреса возврата не создаётся. До входа общего рисователя
остальные регистры, флаги и SP сохраняются.

Должна быть выбрана страница станционного кода в окне #C000.
В этом контексте цель #C2DF является [DrawCenteredItem](CenteredItem.md).
Та же числовая цель при другом банке не имеет этого договора.

При полном возврате HL содержит загруженный индекс, DE и BC восстановлены,
A=#C3, F соответствует текстовому выходу общего рисователя. Рабочими
остаются младший L' и AF'. H', DE', BC', IX, IY, I и IFF сохраняются.
Остальные изменения bitmap, карты и текстового окна описаны в CenteredItem.md.

## Проверка

[CheckDrawAdapters.py](../Tools/Disasm/Research/CheckDrawAdapters.py)
восстанавливает настоящий перенос станционного кода из дисковых смещений
#05CE..#2237 по адресам #6322..#7F8B. Затем исполняет исходный цикл
загрузчика и проверяет изменяемые слова всех 46 обработчиков.

Для 21 обёртки проведены 10752 проверки входа в общий рисователь,
включая все 256 входных F и два произвольных прежних HL. Сверяются
переданный индекс и сохранение остальных регистров, флагов и SP.
Полный рисователь проверен отдельной моделью в CenteredItem.md.
Страница 0 является условием фикстуры, аппаратное переключение банков
и настоящий IRQ здесь не исполняются. Нативный запуск не подтверждён.
Отчёт [DrawAdapterVerification.json](../Tools/Disasm/Reports/DrawAdapterVerification.json).

## Включение и отключение по списку

[DisableDrawList](../Source/Station/DisableDrawList.asm), #9C59,
пишет RET #C9 в первый байт каждого обработчика списка.
[EnableDrawList](../Source/Station/EnableDrawList.asm), #9C68,
восстанавливает LD HL,nn #21. Слово индекса и следующие три байта JP не меняются.
Первые байты 21 установленных обёрток названы DrawItemState.OpcodeNN.

В отключённом состоянии обёртка исполняет один RET. Все регистры и F,
включая первоначальный HL, сохраняются. Общий рисователь не вызывается,
не требуется подготовка его окна. Включение восстанавливает конкретный
код LD HL,nn, произвольный прежний первый байт не сохраняется.

Список состоит из двухбайтовых FDrawListEntry.Handler. Проверяется только
старший байт указателя. Значение 1 завершает обход при любом младшем байте,
поэтому вся область указателей #0100..#01FF воспринимается как ограничитель.
Встроенного лимита 128 записей нет. Список должен достигать ограничителя,
цели должны быть доступны для записи и не перекрывать исполняемый обход,
его список или стек.

Оба обработчика возвращают HL на старший байт ограничителя,
E равен его младшему байту. D содержит старший байт последней цели,
при пустом списке сохраняет прежнее значение. BC сохраняется,
A=0,F=#42 OR входной Carry. Альтернативные и индексные регистры,
I и IFF сохраняются, стек сбалансирован.

[CheckDrawListPatches.py](../Tools/Disasm/Research/CheckDrawListPatches.py)
проверил 134192 случая, все младшие байты ограничителя и входные F
на пустом списке, длины 1..128, 256 и 512. Сравнивается точный набор
записанных адресов. Дополнительно CheckDrawAdapters.py исполняет оба
обработчика на списке настоящих обёрток и проверяет 10752 отключённых
вызова с полным сохранением регистров, затем восстановление LD HL.
Отчёт [DrawListPatchVerification.json](../Tools/Disasm/Reports/DrawListPatchVerification.json).

## Связанные исходники

| Вход | Процедура |
| --- | --- |
| #7A15 | [Station.DrawItem30](../Source/Station/DrawItem30.asm) |
| #7A55 | [Station.DrawSaleModeButton](../Source/Station/DrawSaleModeButton.asm) |
| #7A82 | [Station.DrawPurchaseModeButton](../Source/Station/DrawPurchaseModeButton.asm) |
| #7A9E | [Station.DrawItem09](../Source/Station/DrawItem09.asm) |
| #7AB4 | [Station.DrawItem02](../Source/Station/DrawItem02.asm) |
| #7B0B | [Station.DrawItem03](../Source/Station/DrawItem03.asm) |
| #7B25 | [Station.DrawEquipmentPurchase](../Source/Station/DrawEquipmentPurchase.asm) |
| #7B40 | [Station.DrawEquipmentSale](../Source/Station/DrawEquipmentSale.asm) |
| #7B51 | [Station.DrawFlightButton](../Source/Station/DrawFlightButton.asm) |
| #7C7E | [Station.DrawItem14](../Source/Station/DrawItem14.asm) |
| #7CB6 | [Station.DrawItem15](../Source/Station/DrawItem15.asm) |
| #7CF8 | [Station.DrawContractButton](../Source/Station/DrawContractButton.asm) |
| #7D24 | [Station.DrawItem17](../Source/Station/DrawItem17.asm) |
| #7D53 | [Station.DrawItem16](../Source/Station/DrawItem16.asm) |
| #7D77 | [Station.DrawSellControl](../Source/Station/DrawSellControl.asm) |
| #7D99 | [Station.DrawItem04](../Source/Station/DrawItem04.asm) |
| #7DB5 | [Station.DrawItem05](../Source/Station/DrawItem05.asm) |
| #7DE1 | [Station.DrawItem06](../Source/Station/DrawItem06.asm) |
| #7E19 | [Station.DrawShipControl](../Source/Station/DrawShipControl.asm) |
| #7F11 | [Station.DrawItem08](../Source/Station/DrawItem08.asm) |
| #AA4F | [Station.DrawItem33](../Source/Station/DrawItem33.asm) |
