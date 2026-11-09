# Новые входы действий интерфейса и банковые продолжения

Исходный DispatchInterfaceEvent передаёт управление по EventHandler+3, минуя трёхбайтовую обёртку. Проверка 46 записей обнаружила 19 прежде непокрытых входов. Таблица ниже приводит действующие имена этих входов и найденных помощников. Точные договоры и границы проверки указаны в исходниках.

Дополнительный D0C3 подтверждён вызовом из DrawMapPanelContents по 6D58 после выбора банка 1 и двух помощников, сохраняющих этот банк.

| Регион | Адрес | Новый исходник | Байтов |
| --- | --- | --- | --- |
| Station | 6774 | [HandleShipModelAction](../Source/Station/HandleShipModelAction.asm) | 12 |
| Station | 67A9 | [ShipModelChoice](../Source/Station/ShipModelChoice.asm) | 39 |
| Station | 683A | [HandleModelPreviewClick](../Source/Station/HandleModelPreviewClick.asm) | 53 |
| Station | 6916 | [HandleModelDescriptionClick](../Source/Station/HandleModelDescriptionClick.asm) | 39 |
| Station | 6963 | [CountModelDescriptionRows](../Source/Station/CountModelDescriptionRows.asm) | 21 |
| Station | 697B | [HandleHelpTextAction](../Source/Station/HandleHelpTextAction.asm) | 44 |
| Station | 69E0 | [HandleHelpContentsAction](../Source/Station/HandleHelpContentsAction.asm) | 107 |
| Station | 6A86 | [HandleEquipmentInfoAction](../Source/Station/HandleEquipmentInfoAction.asm) | 40 |
| Station | 6AAF | [TryDrawEquipmentInfo](../Source/Station/TryDrawEquipmentInfo.asm) | 7 |
| Station | 6AEC | [HandleEnvironmentAction](../Source/Station/HandleEnvironmentAction.asm) | 162 |
| Station | 6B9E | [TryDrawEnvironmentPanel](../Source/Station/TryDrawEnvironmentPanel.asm) | 7 |
| Station | 6C0D | [HandleMapPanelEvent](../Source/Station/HandleMapPanelEvent.asm) | 310 |
| Station | 6D44 | [RefreshMapPanel](../Source/Station/RefreshMapPanel.asm) | 10 |
| Station | 6D4E | [ClearAndDrawMapPanel](../Source/Station/ClearAndDrawMapPanel.asm) | 10 |
| Station | 6DC5 | [HandleDecodedMessageClick](../Source/Station/HandleDecodedMessageClick.asm) | 14 |
| Station | 6E82 | [HandleQueuedMessageClick](../Source/Station/HandleQueuedMessageClick.asm) | 7 |
| Station | 6FF1 | [HandleTradePanelClick](../Source/Station/HandleTradePanelClick.asm) | 83 |
| Station | 7175 | [HandleEquipmentListAction](../Source/Station/HandleEquipmentListAction.asm) | 155 |
| Station | 7220 | [TryDrawEquipmentList](../Source/Station/TryDrawEquipmentList.asm) | 7 |
| Station | 7421 | [HandleSaveSlotAction](../Source/Station/HandleSaveSlotAction.asm) | 97 |
| Station | 74AA | [HandleLoadSlotAction](../Source/Station/HandleLoadSlotAction.asm) | 97 |
| Station | 759C | [HandleGameSettingsAction](../Source/Station/HandleGameSettingsAction.asm) | 132 |
| Station | 7630 | [TryDrawGameSettings](../Source/Station/TryDrawGameSettings.asm) | 7 |
| Station | 7679 | [HandleSystemInfoAction](../Source/Station/HandleSystemInfoAction.asm) | 14 |
| Station | 783B | [HandleSystemMapAction](../Source/Station/HandleSystemMapAction.asm) | 73 |
| Station | 7885 | [TryDrawVariantPanel](../Source/Station/TryDrawVariantPanel.asm) | 7 |
| Station | 794B | [HandleWelcomeAction](../Source/Station/HandleWelcomeAction.asm) | 9 |
| Station | A191 | [ParseSettingsLabel](../Source/Station/ParseSettingsLabel.asm) | 69 |
| Station | A1D6 | [ScrollWindowRows](../Source/Station/ScrollWindowRows.asm) | 153 |
| Station | A26F | [XorRowIfSelected](../Source/Station/XorRowIfSelected.asm) | 17 |
| Station | AA58 | [HandleMissionGroupAction](../Source/Station/HandleMissionGroupAction.asm) | 42 |
| Station | BE27 | [MoveItemToTailIfListed](../Source/Station/MoveItemToTailIfListed.asm) | 17 |
| Station | C6B0 | [ClearScrollWindowBody](../Source/Station/ClearScrollWindowBody.asm) | 430 |
| Map | C368 | [SumSquares8](../Source/Map/SumSquares8.asm) | 36 |
| Map | C38C | [SelectNearestVisiblePoint](../Source/Map/SelectNearestVisiblePoint.asm) | 131 |
| Map | C4E5 | [BuildVisibleMapPoints](../Source/Map/BuildVisibleMapPoints.asm) | 259 |
| Map | C5E8 | [SelectNearestMapVariant](../Source/Map/SelectNearestMapVariant.asm) | 107 |
| Map | C653 | [UpdateMapDistanceMinimum](../Source/Map/UpdateMapDistanceMinimum.asm) | 36 |
| Map | D0C3 | [SetupMapRasterWindow](../Source/Map/SetupMapRasterWindow.asm) | 233 |

Исходная статическая проверка фиксирует физические инструкции и основания для выбора корней. [StationEventRootsAudit](../Tools/Disasm/Reports/StationEventRootsAudit.json) · [MapEventRootsAudit](../Tools/Disasm/Reports/MapEventRootsAudit.json).

## Дополнительные входы в существующих файлах

Дополнительный вход KeepSelector по CBE2 разобран в [RepaintChain](RepaintChain.md), ShowBase по A499 в [ScreenUpdate](ScreenUpdate.md).
- [Station.RepaintAndTrack.KeepSelector](../Source/Station/RepaintAndTrack.asm), адрес CBE2.
- [Station.EndScreenUpdate.ShowBase](../Source/Station/EndScreenUpdate.asm), адрес A499.
