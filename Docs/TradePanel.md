# Торговая панель

Разбор связывает рисунок, динамическую высоту подсветки, выбранную строку, прокрутку и код события интерпретатора. Исходные байты сохранены. Участок 7044..7070 разделён на банковую обёртку 29 байтов и наведение 16 байтов по фактической границе 7061. [Отчёт разделения](../Tools/Disasm/Reports/TradePanelSplitVerification.json).

| Вход | Адрес | Назначение |
| --- | --- | --- |
| [HandleTradePanelHover](../Source/Station/HandleTradePanelHover.asm) | 6FEE | Event, хвостовое наведение |
| [HandleTradePanelClick](../Source/Station/HandleTradePanelClick.asm) | 6FF1 | Event+3, действие |
| [RunTradeEventAndRedraw](../Source/Station/RunTradeEventAndRedraw.asm) | 7044 | событие, LANG и перерисовка |
| [UpdateTradeRowHover](../Source/Station/UpdateTradeRowHover.asm) | 7061 | динамическая высота и выбор строки |
| [DrawTradePanel](../Source/Station/DrawTradePanel.asm) | 7071 | рамка, заголовок и колонки |
| DrawTradePanel.DrawColumns | 708E | дополнительный callback только колонок |
| DrawTradePanel.FinishCounts | 7091 | возврат и запись счётчика |

## Операнды и состояние

ScriptSelection.CargoBase по 7026 является словом начального индекса внутри LD HL. Рисователь и прокрутка читают оба байта, [GetCargoIndex](../Source/Text/GetCargoIndex.asm) использует только младший байт вместе с CargoRow. Это различие сохранено.

TradePanelState.HoverArea по 7062 является словом LD DE, исходно 1E23. Младший байт задаёт отступ 35 пикселей, старший HoverRows по 7063 первоначально 30 строк, но затем изменяется рисователем. ScriptSelection.CargoRow по 7068 является прежним номером либо FF. Это числовые поля и отдельный маркер, не флаговый байт.

Opcode по 7071 содержит исходный LD HL либо временный RET отключения. ItemIndex по 7072 устанавливает загрузчик. EventCode по 983A является байтовым кодом для торгового ReadEventCode. Новые области под эти имена не выделяются.

## Рисунок и высота подсветки

Активный Entry вызывает DrawCaptionItem, [SetMarketTextColumns](../Source/Station/SetMarketTextColumns.asm), сбрасывает CargoRow=FF и печатает заголовок EBF3. Обменами AF статус заголовка сохраняется в основном наборе, AF' становится 0044.

При Carry от заголовка числа пропускаются. Иначе HL получает полное CargoBase и исполнение входит в DrawColumns. Этот дополнительный вход вызывается также из [ScrollWindowRows](../Source/Station/ScrollWindowRows.asm), он принимает уже настроенное окно и HL индекса без повторной рамки и заголовка.

DrawColumns вызывает [DrawTradeNumericColumns](../Source/Station/DrawTradeNumericColumns.asm). Его A' считает начатые строки, включая строку с отказом первого глифа. FinishCounts обменивает основной и альтернативный AF, возвращает счётчик в A и записывает его в HoverRows. При пропуске чисел AF=0044 и HoverRows=0. При числовом проходе HL, DE, BC принадлежат числовому рисователю, AF' получает его основной статус, основной AF содержит счётчик.

Первый RET C9 отключает только Entry и сохраняет состояние. Он не отключает callback DrawColumns по 708E. См. [общие обёртки](DrawAdapters.md). Дополнительный FinishCounts по 7091 получает счётчик в AF', меняет наборы местами, записывает A и возвращается с тем же адресом вызывающего.

## Наведение

HandleTradePanelHover передаёт возврат UpdateTradeRowHover без нового CALL. Читаются DE из HoverArea и A из CargoRow, точный DrawTradePanel должен быть последним рисователем списка. UpdateRowHover переводит D строк в пиксели по модулю 256 и ограничивает ClampRowHeight. E остаётся верхним отступом.

Только при Z=0 весь возвращённый A записывается в CargoRow. Нулевая успешно выбранная строка тоже записывается. Z=1 сохраняет прежний номер. D=0 отключает попадание, D=32 тоже превращается в нулевой запрос. Служебный результат позднего отказа повторной проверки PointerY не исправляется, см. [RowHover](RowHover.md).

## Действие и прокрутка

Сначала RepaintAndFlag. Его Carry завершает действие, в том числе после уже выполненной перерисовки. При Carry=0 селектор 1 проверяет CargoRow только на FF, отдельного сравнения с HoverRows нет. Без строки возврат, иначе байтовый `X=(PointerX-OriginXLow) AND FF` выбирает событие 10 при X<135 и событие 9 при X>=135. Слева колонки «Продажа», справа «Наличие». Отрицательное смещение оборачивается.

Прочие селекторы вызывают CloseMenuOnRow. При совпадении символьных строк PointerY и OriginYLow удаляются основная панель и затем элемент по DrawItemState.Index35. Его TextIndex=13 в CenterTextBase задаёт текст «Продать товар» и «Продать только маркированный товар», это единый управляющий элемент продажи. Его общий callback вызывает событие 11 для выбранного вида груза и после перерисовки устанавливает строку 0 независимо от результата сценария, см. [ControlPanelGroups](ControlPanelGroups.md).

При несовпавшей строке задаются торговые колонки, [XorRowIfSelected](../Source/Station/XorRowIfSelected.asm) снимает прежнюю полосу, CargoRow=FF. Настраиваются RenderCall=DrawColumns, EndLimit=29, A=32, HL из CargoBase. После ScrollWindowRows итоговый HL записывается обратно в слово CargoBase. Полный цикл с этим настоящим callback проверен в [ScrollWindow](ScrollWindow.md).

Событие передаётся хвостовому RunTradeEventAndRedraw с прежним возвратом. Для левой колонки выполняется JR на соседний вход, для правой DEC A преобразует 10 в 9 и далее следует последовательное исполнение следующего файла. Жёсткий порядок include (0),(1) сохранён, лишний JP не добавлен.

## Банковый вызов и экран

RunTradeEventAndRedraw сохраняет A в EventCode и выбирает LANG банка 6 через SelectRamBank. [RunMarketScript](../Source/Text/RunMarketScript.asm) всегда начинает с CA8F. Код события не является адресом или номером начала сценария, команды читают его через [ReadEventCode](../Source/Text/ReadEventCode.asm). Первые два выбора банка сохраняют старшие управляющие биты старой тени.

После сценария выбран банк 0, выполняются BeginScreenUpdate, [DrawItem00](../Source/Station/DrawItem00.asm), DrawTradePanel и EndScreenUpdate. В конце A=10, F от торгового рисователя, при активном Entry это флаги счётчика. База показана, указатель возобновлён, UpdateBlocked=0. HL, DE, BC остаются результатом последнего активного рисователя либо сценария, экранные обёртки сохраняют эти пары. Изменения IX и прочих регистров сценария отдельным кадром не отменяются.

Исходный сценарий устанавливает 9 как покупку одной единицы, 10 как продажу одной, 11 как продажу всего текущего груза. Эти ветви исполнены в 4912 конфигурациях, особенности Q и продолжающей команды m сохранены, см. [OriginalTradeScript](OriginalTradeScript.md). Рыночный bit7 запрещает продажу со штрафом и списанием количества груза. Игровая роль bit7 именно грузового массива и все его писатели ещё требуют разбора. Визуальный вывод FE по обоим старшим разрядам установлен в [TradeNumericColumns](TradeNumericColumns.md).

## Проверки

- [Рисователь](../Tools/Disasm/Research/CheckTradePanelDraw.py), 48 активных проходов и 256 отключённых Entry. Независимый bitmap заголовка и числового тела после реальной рамки, счётчик, сброс строки и конечные пары. [Отчёт](../Tools/Disasm/Reports/TradePanelDrawVerification.json).
- [Наведение](../Tools/Disasm/Research/CheckTradePanelHover.py), 7680 проходов, все байты запроса и все Y на основных значениях. Настоящие XOR и указатель, независимый bitmap. [Отчёт](../Tools/Disasm/Reports/TradePanelHoverVerification.json).
- [Действие](../Tools/Disasm/Research/CheckTradePanelEvent.py), 66560 вариантов колонки, каждый X и OriginXLow, и 1024 общие развилки. Реальные списки и снятие полосы, остановка на входах сценария и отдельно проверенной прокрутки. [Отчёт](../Tools/Disasm/Reports/TradePanelEventVerification.json).
- [Банковая обёртка](../Tools/Disasm/Research/CheckTradeScriptWrapper.py), 32 прохода с реальным интерпретатором и явно пустым NUL-сценарием в моделируемом LANG. Проверены вызовы, порты, активный и отключённый статус и торговая рамка. Исходные команды торговли здесь не исполняются, сделки не подтверждаются. [Отчёт](../Tools/Disasm/Reports/TradeScriptWrapperVerification.json).

HALT пробуждается явно. Аппаратные IRQ, нативная торговля и сборка этими моделями не подтверждены. Неизвестные игровые значения остаются явно обозначенными.
