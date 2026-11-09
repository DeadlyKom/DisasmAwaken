# Подписи интерфейса и общие ограничители

В банке станции 0 выделен ещё 3351 исходный байт текстов. Все CP866-коды, пробелы, пустые записи, колонки 02..06 и исходные ошибки написания сохранены. Никакие строки не перекодируются при сборке.

| Адреса | Ресурс | Потребитель |
|---|---|---|
| E39A..E4A9 | [CaptionLabels.bin](../Source/Station/Resources/CaptionLabels.bin) | [DrawCaptionItem](../Source/Station/DrawCaptionItem.asm) |
| E4AA..EA3A | [CenteredItemTexts.bin](../Source/Station/Resources/CenteredItemTexts.bin) | [DrawCenteredItem](../Source/Station/DrawCenteredItem.asm) |
| EA3B..EA88 | [LegalStatusLabels.bin](../Source/Station/Resources/LegalStatusLabels.bin) | [DrawItem00](../Source/Station/DrawItem00.asm) |
| EA89..EA9A | [StatusFieldLabels.bin](../Source/Station/Resources/StatusFieldLabels.bin) | [DrawItem00](../Source/Station/DrawItem00.asm) |
| EA9B..EB81 | [SystemInfoTemplate.bin](../Source/Station/Resources/SystemInfoTemplate.bin) | [DrawSystemInfoPanel](../Source/Station/DrawSystemInfoPanel.asm) |
| EB82..EB8C | [NoPlanetsText.bin](../Source/Station/Resources/NoPlanetsText.bin) | [DrawSystemInfoPanel](../Source/Station/DrawSystemInfoPanel.asm) |
| EB8D..EBC1 | [GovernmentLabels.bin](../Source/Station/Resources/GovernmentLabels.bin) | [PrintSystemTraits](../Source/Station/PrintSystemTraits.asm) |
| EBC2..EBF2 | [EconomyLabels.bin](../Source/Station/Resources/EconomyLabels.bin) | [PrintSystemTraits](../Source/Station/PrintSystemTraits.asm) |
| EBF3..EC4B | [TradeHeadings.bin](../Source/Station/Resources/TradeHeadings.bin) | [DrawTradePanel](../Source/Station/DrawTradePanel.asm) |
| EC4C..EE18 | [TradeGoodsLabels.bin](../Source/Station/Resources/TradeGoodsLabels.bin) | [DrawTradeNumericColumns](../Source/Station/DrawTradeNumericColumns.asm) |
| EE19..EE56 | [EquipmentHeadings.bin](../Source/Station/Resources/EquipmentHeadings.bin) | [DrawEquipmentList](../Source/Station/DrawEquipmentList.asm) |
| EE57..F065 | [EquipmentNames.bin](../Source/Station/Resources/EquipmentNames.bin) | [PrintEquipmentRows](../Source/Station/PrintEquipmentRows.asm) |
| F0B2..F0FC | [PoliticalAreaLabels.bin](../Source/Station/Resources/PoliticalAreaLabels.bin) | [DrawSystemInfoPanel](../Source/Station/DrawSystemInfoPanel.asm) |

[Физический реестр](../Tools/Disasm/Reports/StationInterfaceTextLayout.json), [точные тексты](../Tools/Disasm/Research/Evidence/StationInterfaceTexts.txt), [разметка](../Tools/Disasm/Research/StationInterfaceTextResources.py), [публикация](../Tools/Disasm/Research/ClassifyStationInterfaceTextResources.py). Последовательность ресурсов задаёт [04_STATIONF.inc](../Source/Files/04_STATIONF.inc).

## Один LF на два потока

CaptionTextBase равен E399, это конечный LF последней строки контекстного меню. По E39A расположен ещё один LF. Поэтому нулевой индекс заголовка выбирает пустую строку, индексы 1..21 выбирают реальные заголовки. Например, 20 выбирает «Внимание!», 21 выбирает «Добро пожаловать!». Новая разметка не исправляет эту последовательность и не сдвигает существующие индексы.

Последняя строка CaptionLabels завершается LF по E4AA, принадлежащим началу CenteredItemTexts. Аналогично строка прототипа интерфейса из LegalStatusLabels заканчивается начальным LF StatusFieldLabels по EA89. Фраза «Планет нет.» использует начальный LF GovernmentLabels по EB8D, а последняя подпись строя использует начальный LF EconomyLabels по EBC2. Ресурс нельзя переставлять отдельно от следующего потока либо дописывать ему второй ограничитель.

CenteredItemTexts содержит пустые LF-записи и многострочные описания с CR. Их наличие сохраняется, но не объявляется доступностью каждого пункта в игре. EquipmentNames содержит 33 CR-подписи, включая «Совет» и два «Анекдот». Это физические записи, а не доказательство существования 33 разных работающих видов оснащения.

## Проверка выбора

[CheckStationPhysicalTextSelectors.py](../Tools/Disasm/Research/CheckStationPhysicalTextSelectors.py) исполняет исходные SkipLfRecords и SkipCrRecords на настоящем содержимом банков. Независимый поиск разделителей задаёт ожидаемые адреса. [Отчёт](../Tools/Disasm/Reports/StationPhysicalTextSelectorsVerification.json) содержит каждый проверенный индекс и строку. Проверяются также Carry, сохраняемые регистры, возврат SP и отсутствие записей вне CPU-стека. Это проверка поиска, не аппаратных прерываний, рисования, времени либо полного игрового процесса.

Соседние F066..F0B1 содержат [подпись топлива и шаблон доставки](StationDetachedText.md).
Их читает [печататель второго списка](SecondaryEquipmentRows.md).
Путь штатного открытия второго списка пока неизвестен.
