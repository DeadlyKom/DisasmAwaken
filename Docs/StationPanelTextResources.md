# Исходные текстовые потоки панелей станции

Из STATIONF выделены 5015 байтов с установленными текстовыми потребителями. Адреса ниже относятся к банку станции 0. Исходная CP866, ошибки написания, CR, LF и прочие байты сохранены. UTF-8 расшифровка служит только для чтения и не участвует в сборке.

| Адреса CPU | Байтов | Ресурс | Разметка | Потребитель |
|---|---|---|---|---|
| CE19..D1B9 | 929 | [QueuedMessages.bin](../Source/Station/Resources/QueuedMessages.bin) | Начальный LF и 17 сообщений до LF | [DrawQueuedMessagePanel](../Source/Station/DrawQueuedMessagePanel.asm) |
| D1BA..DE52 | 3225 | [EquipmentDescriptions.bin](../Source/Station/Resources/EquipmentDescriptions.bin) | Начальный LF и 34 описания до LF | [UpdateEquipmentInfo](../Source/Station/UpdateEquipmentInfo.asm) |
| DE53..DE8E | 60 | [SaveSlotLabels.bin](../Source/Station/Resources/SaveSlotLabels.bin) | Пять подписей, четыре CR, конечный LF | [DrawSaveSlotPanel](../Source/Station/DrawSaveSlotPanel.asm) |
| DE8F..DECA | 60 | [LoadSlotLabels.bin](../Source/Station/Resources/LoadSlotLabels.bin) | Пять подписей, четыре CR, конечный LF | [DrawLoadSlotPanel](../Source/Station/DrawLoadSlotPanel.asm) |
| DECB..DF3B | 113 | [EnvironmentLabels.bin](../Source/Station/Resources/EnvironmentLabels.bin) | Начальный CR, 13 подписей, конечный LF | [PrintEnvironmentRows](../Source/Station/PrintEnvironmentRows.asm) |
| DF3C..E0E3 | 424 | [GameSettingsLabels.bin](../Source/Station/Resources/GameSettingsLabels.bin) | Начальный CR, 43 подписи, включая пустые по смыслу строки из пробела, конечный LF | [PrintGameSettingsRows](../Source/Station/PrintGameSettingsRows.asm) |
| E262..E32D | 204 | [DecodedMessages.bin](../Source/Station/Resources/DecodedMessages.bin) | Начальный LF и два сообщения до LF | [PrintDecodedMessage](../Source/Station/PrintDecodedMessage.asm) |

[Реестр](../Tools/Disasm/Reports/StationPanelTextLayout.json) содержит адрес, длину и точные байты текста каждой записи в читаемом представлении. [Полная расшифровка](../Tools/Disasm/Research/Evidence/StationPanelTexts.txt), [описание диапазонов](../Tools/Disasm/Research/StationPanelTextResources.py), [проверенная публикация](../Tools/Disasm/Research/ClassifyStationPanelTextResources.py). Физический порядок задаёт [04_STATIONF.inc](../Source/Files/04_STATIONF.inc).

В описании оснащения по D8C9 находится исходный байт 15, он не заменён ожидаемой буквой. PrintText обрабатывает отдельно коды меньше семи и CR, поэтому 15 проходит по пути глифа. Назначение изображения этого глифа не выводится из похожести фразы.

Граница списка не заменяет проверку игрового селектора. Процедуры поиска LF не ограничивают произвольный индекс числом записей. Для всех 17 уведомлений выполняется отдельная модель исходного вывода с независимым расчётом bitmap. Модель оснащения выполняет 408 проверок поиска и подсчёта строк всех 34 физических описаний. Полный вывод, прокрутка и игровые ветви выбора имеют собственные границы проверки, наличие 34 записей не означает проверки каждого игрового сценария. Два сообщения расшифровки имеют отдельную модель. Подписи и их вывод описаны в [SettingsRowPanels](SettingsRowPanels.md), [SaveLoadPanels](SaveSlots.md), [DecodedMessage](DecodedMessage.md), [MessagePanels](MessagePanels.md) и [EquipmentInfo](EquipmentInfo.md).

Соседние E0E4..E261, 382 байта, сохранены как [Unclassified80E4_8262.bin](../Source/Resources/04_STATIONF/Unclassified80E4_8262.bin). Читаются имена абонентов и систем с кодом колонки 02, но потребитель этого списка пока не установлен. Это не подтверждённый каталог игровой связи.

Числовые CALL DB00, DB05, DB08 и E0xx из других банков не являются обращениями к этим текстам. Они исключены из доказательства назначения. Сборка, аппаратные прерывания и нативный игровой процесс этой классификацией не проверяются.

[Заголовки и подписи интерфейса](StationInterfaceTextResources.md) выделены отдельно с сохранением общих LF соседних потоков.
