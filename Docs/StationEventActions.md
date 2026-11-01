# Новые входы действий интерфейса и банковые продолжения

Исходный DispatchInterfaceEvent передаёт управление по EventHandler+3, минуя трёхбайтовую обёртку. Проверка фактических 46 записей обнаружила 19 прежде непокрытых входов. Их прямые пути дают новые станционные инструкции и вызовы банка карты. Это восстановление достижимости и физических инструкций, большинство алгоритмов перечисленных ниже фрагментов остаются Unknown. SumSquares8, SetupMapRasterWindow, UpdateMapDistanceMinimum, SelectNearestMapVariant, BuildVisibleMapPoints и SelectNearestVisiblePoint разобраны с явными контрактами и границами моделей. Ручные исходники не перевыпускаются.

Дополнительный D0C3 подтверждён вызовом из Unknown6D58 после выбора банка 1 и двух разобранных помощников без переключения банков. Неопределённый банковый контекст не заменяется предположением по одному CPU-адресу.

| Регион | Адрес | Новый исходник | Байтов |
| --- | --- | --- | --- |
| Station | 6774 | [Unknown6774](../Source/Station/HandleShipModelAction.asm) | 12 |
| Station | 67A9 | [Unknown67A9](../Source/Station/ShipModelChoice.asm) | 39 |
| Station | 683A | [HandleModelPreviewClick](../Source/Station/HandleModelPreviewClick.asm) | 53 |
| Station | 6916 | [HandleModelDescriptionClick](../Source/Station/HandleModelDescriptionClick.asm) | 39 |
| Station | 6963 | [CountModelDescriptionRows](../Source/Station/CountModelDescriptionRows.asm) | 21 |
| Station | 697B | [Unknown697B](../Source/Station/HandleHelpTextAction.asm) | 44 |
| Station | 69E0 | [Unknown69E0](../Source/Station/HandleHelpContentsAction.asm) | 107 |
| Station | 6A86 | [Unknown6A86](../Source/Station/HandleEquipmentInfoAction.asm) | 40 |
| Station | 6AAF | [Unknown6AAF](../Source/Station/TryDrawEquipmentInfo.asm) | 7 |
| Station | 6AEC | [Unknown6AEC](../Source/Station/HandleEnvironmentAction.asm) | 162 |
| Station | 6B9E | [Unknown6B9E](../Source/Station/TryDrawEnvironmentPanel.asm) | 7 |
| Station | 6C0D | [HandleMapPanelEvent](../Source/Station/HandleMapPanelEvent.asm) | 310 |
| Station | 6D44 | [RefreshMapPanel](../Source/Station/RefreshMapPanel.asm) | 10 |
| Station | 6D4E | [ClearAndDrawMapPanel](../Source/Station/ClearAndDrawMapPanel.asm) | 10 |
| Station | 6DC5 | [HandleDecodedMessageClick](../Source/Station/HandleDecodedMessageClick.asm) | 14 |
| Station | 6E82 | [HandleQueuedMessageClick](../Source/Station/HandleQueuedMessageClick.asm) | 7 |
| Station | 6FF1 | [HandleTradePanelClick](../Source/Station/HandleTradePanelClick.asm) | 83 |
| Station | 7175 | [Unknown7175](../Source/Station/HandleEquipmentListAction.asm) | 155 |
| Station | 7220 | [Unknown7220](../Source/Station/TryDrawEquipmentList.asm) | 7 |
| Station | 7421 | [Unknown7421](../Source/Station/HandleSaveSlotAction.asm) | 97 |
| Station | 74AA | [Unknown74AA](../Source/Station/HandleLoadSlotAction.asm) | 97 |
| Station | 759C | [Unknown759C](../Source/Station/HandleGameSettingsAction.asm) | 132 |
| Station | 7630 | [Unknown7630](../Source/Station/TryDrawGameSettings.asm) | 7 |
| Station | 7679 | [Unknown7679](../Source/Station/HandleSystemInfoAction.asm) | 14 |
| Station | 783B | [Unknown783B](../Source/Station/HandleSystemMapAction.asm) | 73 |
| Station | 7885 | [TryDrawVariantPanel](../Source/Station/TryDrawVariantPanel.asm) | 7 |
| Station | 794B | [Unknown794B](../Source/Station/HandleWelcomeAction.asm) | 9 |
| Station | A191 | [ParseSettingsLabel](../Source/Station/ParseSettingsLabel.asm) | 69 |
| Station | A1D6 | [ScrollWindowRows](../Source/Station/ScrollWindowRows.asm) | 153 |
| Station | A26F | [XorRowIfSelected](../Source/Station/XorRowIfSelected.asm) | 17 |
| Station | AA58 | [UnknownAA58](../Source/Station/HandleMissionGroupAction.asm) | 42 |
| Station | BE27 | [MoveItemToTailIfListed](../Source/Station/MoveItemToTailIfListed.asm) | 17 |
| Station | C6B0 | [ClearScrollWindowBody](../Source/Station/ClearScrollWindowBody.asm) | 430 |
| Map | C368 | [SumSquares8](../Source/Map/SumSquares8.asm) | 36 |
| Map | C38C | [SelectNearestVisiblePoint](../Source/Map/SelectNearestVisiblePoint.asm) | 131 |
| Map | C4E5 | [BuildVisibleMapPoints](../Source/Map/BuildVisibleMapPoints.asm) | 259 |
| Map | C5E8 | [SelectNearestMapVariant](../Source/Map/SelectNearestMapVariant.asm) | 107 |
| Map | C653 | [UpdateMapDistanceMinimum](../Source/Map/UpdateMapDistanceMinimum.asm) | 36 |
| Map | D0C3 | [SetupMapRasterWindow](../Source/Map/SetupMapRasterWindow.asm) | 233 |

Сборка и исполнение новых ветвей не выполнялись. Совпадение инструкций с исходными байтами не доказывает полной семантики. Исходные разметки и причины корней находятся в [StationEventRootsAudit](../Tools/Disasm/Reports/StationEventRootsAudit.json) и [MapEventRootsAudit](../Tools/Disasm/Reports/MapEventRootsAudit.json).

## Дополнительные входы в существующих файлах

Существующие инструкции сохранены. Дополнительный вход KeepSelector по CBE2 разобран в [RepaintChain](RepaintChain.md), ShowBase по A499 в [ScreenUpdate](ScreenUpdate.md). Остальные новые действия и помощники ниже сохраняют свои Unknown до отдельного разбора.
- [Station.RepaintAndTrack.KeepSelector](../Source/Station/RepaintAndTrack.asm), адрес CBE2.
- [Station.EndScreenUpdate.ShowBase](../Source/Station/EndScreenUpdate.asm), адрес A499.
