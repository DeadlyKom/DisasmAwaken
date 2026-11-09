# Физические состояния SAVE

Файлы SAVE0..SAVE5 содержат по 512 байтов. Их адрес загрузки
определяется инструкциями [загрузчика](../Source/Station/HandleLoadSlotAction.asm)
и [записи](../Source/Station/HandleSaveSlotAction.asm), это #983B..#9A3A.
Параметр каталога #6000 эти обработчики не используют.

SAVE0..SAVE4 отличаются от исходного блока STATIONF только байтом +3,
то есть FStationBcdCounter.Low. Значения SAVE0..SAVE4 равны #15, #17,
#19, #22 и #25. В STATIONF этот байт равен #10. SAVE5 целиком нулевой.
Нулевой SAVE5 сохраняется в исходном виде, пригодность такого состояния
для игры не установлена. В том числе его границы списков равны нулю,
а не исходному #80. Нормализация либо исправление не выполняются.

В каждом файле 473 байта оформлены существующими структурами, 29 байтов
составляют физический хвост переноса, 10 байтов остаются в неизвестных
диапазонах. Поля Unknown внутри известных
структур сохраняют неизвестный смысл. Размер и порядок всех полей
следуют из уже разобранных потребителей станции, новых адресов нет.

| Смещение SAVE | Длина | Поля станции |
| --- | --- | --- |
| #000 | 4 | [StationTimer.asm](../Source/Station/Data/StationTimer.asm) |
| #004 | 5 | [CurrentSignature.asm](../Source/Station/Data/CurrentSignature.asm) |
| #009 | 5 | [SelectedMapKey.asm](../Source/Station/Data/SelectedMapKey.asm) |
| #00E | 9 | [PlayerSaveHeader.asm](../Source/Station/Data/PlayerSaveHeader.asm) |
| #017 | 60 | [OwnedCargoRows.asm](../Source/Station/Data/OwnedCargoRows.asm) |
| #053 | 30 | [EquipmentQuantityCodes.asm](../Source/Station/Data/EquipmentQuantityCodes.asm) |
| #071 | 4 | [PrimaryQuantityTail.asm](../Source/Station/Data/PrimaryQuantityTail.asm) |
| #075 | 16 | [MissionOffer.asm](../Source/Station/Data/MissionOffer.asm) |
| #085 | 6 | [Unclassified38C0_38C6.bin](../Source/Resources/04_STATIONF/Unclassified38C0_38C6.bin) |
| #08B | 48 | [OrderCompatibleSlots.asm](../Source/Station/Data/OrderCompatibleSlots.asm) |
| #0BB | 14 | [SecondaryQuantities.asm](../Source/Station/Data/SecondaryQuantities.asm) |
| #0C9 | 2 | [Unclassified3904_3906.bin](../Source/Resources/04_STATIONF/Unclassified3904_3906.bin) |
| #0CB | 1 | [TransitionCounter.asm](../Source/Station/Data/TransitionCounter.asm) |
| #0CC | 1 | [Unclassified3907_3908.bin](../Source/Resources/04_STATIONF/Unclassified3907_3908.bin) |
| #0CD | 1 | [MeasuredDistance.asm](../Source/Station/Data/MeasuredDistance.asm) |
| #0CE | 1 | [Unclassified3909_390A.bin](../Source/Resources/04_STATIONF/Unclassified3909_390A.bin) |
| #0CF | 102 | [StoredMapPoints.asm](../Source/Station/Data/StoredMapPoints.asm) |
| #135 | 11 | [StoredMapOrder.asm](../Source/Station/Data/StoredMapOrder.asm) |
| #140 | 40 | [MapAuxiliaryPoints.asm](../Source/Station/Data/MapAuxiliaryPoints.asm) |
| #168 | 11 | [MapAuxiliaryCodes.asm](../Source/Station/Data/MapAuxiliaryCodes.asm) |
| #173 | 8 | [InterfaceChoices.asm](../Source/Station/Data/InterfaceChoices.asm) |
| #17B | 12 | [PointerKeys.asm](../Source/Station/Data/PointerKeys.asm) |
| #187 | 6 | [InterfaceColors.asm](../Source/Station/Data/InterfaceColors.asm) |
| #18D | 86 | [ControlOptions.asm](../Source/Station/Data/ControlOptions.asm) |
| #1E3 | 29 | [InitialTransferTrailer.bin](../Source/Station/Resources/InitialTransferTrailer.bin) |

Хвост +1E3..+1FF входит в двухсекторные операции SAVE. При переходе в
ACTION он попадает в 9DA0..9DBC. При возврате к станции загрузчик
восстанавливает только первые 481 байт состояния, поэтому свежий STATIONF
сохраняет свой хвост. В модели в него предварительно записали
отличимый набор из 29 байтов и сверили его после вылета, 64 полётных
кадров и на границе обратного переноса. В образе все семь хвостов
сохранены в исходном виде. Назначение отдельных байтов не установлено.
[Проверка](../Tools/Disasm/Reports/StationSaveTransferTrailerVerification.json).

Физические подключения:

- [SAVE1](../Source/Files/11_SAVE1.inc)
- [SAVE2](../Source/Files/12_SAVE2.inc)
- [SAVE3](../Source/Files/13_SAVE3.inc)
- [SAVE4](../Source/Files/14_SAVE4.inc)
- [SAVE5](../Source/Files/15_SAVE5.inc)
- [SAVE0](../Source/Files/16_SAVE0.inc)

[Проверка](../Tools/Disasm/Research/CheckSavedStateLayout.py) сравнивает все
шесть оригинальных файлов и поля существующих структур, обычная статическая
сверка исходников повторно проверяет каждый опубликованный байт.
Это не проверка дисковой аппаратуры, запуска игры или сборки.
