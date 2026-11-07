# Изменяемые инструкции

Это непосредственные записи внутрь размеченных инструкций, включая
отдельно доказанные межмодульные цели. Они включают сохранение SP, операнды и переключаемые
ветви. Не перечисляют все косвенные записи и генерируемые области.

[Проверка путей реестра](../Tools/Disasm/Research/CheckModifiedCodePaths.py)
сверяет 1320 записей, существование указанных исходников и 305 целей с
явными физическими смещениями. У 41 из этих целей недостающие смещения
дополнены по существующему целевому файлу, реальным инструкциям и SourceMap.
Выбранный во время исполнения банк из этого соответствия не выводится,
исходные банковые поля сохранены. Остальные 1015 записей отдельного
target_path не содержат. Такая проверка не устанавливает
все косвенные записи. При согласовании имён исправлены 16 устаревших
путей, адреса записей и исходные инструкции сохранены. Контрольная
подстановка существующего, но неверного целевого файла отвергается без
изменения файлов проекта. Сборка и нативное исполнение не выполняются.

[Дополнение физических целей](../Tools/Disasm/Research/CompleteExplicitMutationTargets.py)
сохраняет отдельный кандидат и исходную версию реестра, затем проверяет,
что все прежние поля каждой записи остались буквально неизменными.

| Регион | Запись из | Адрес записи | Исходная инструкция | Исходник |
| --- | --- | --- | --- | --- |
| Intro | #66B0 | #66EC | `LD BC,#8000` | [DrawScrolledTexture.asm](../Source/Intro/DrawScrolledTexture.asm) |
| Intro | #66BB | #66ED | `LD BC,#8000` | [DrawScrolledTexture.asm](../Source/Intro/DrawScrolledTexture.asm) |
| Intro | #66C4 | #66D4 | `LD HL,#CD40` | [DrawScrolledTexture.asm](../Source/Intro/DrawScrolledTexture.asm) |
| Intro | #66CD | #66D5 | `LD HL,#CD40` | [DrawScrolledTexture.asm](../Source/Intro/DrawScrolledTexture.asm) |
| Intro | #66E2 | #66F8 | `LD SP,#3131` | [SampleTextureRows.asm](../Source/Intro/SampleTextureRows.asm) |
| Intro | #6763 | #6786 | `LD HL,#2121` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #6766 | #678E | `LD IYL,A` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #676F | #6793 | `LD DE,#0000` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #6775 | #679E | `LD HL,#4000` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #678A | #6786 | `LD HL,#2121` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #6799 | #6793 | `LD DE,#0000` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #67A1 | #679E | `LD HL,#4000` | [BuildTextureLookup.asm](../Source/Intro/BuildTextureLookup.asm) |
| Intro | #67F5 | #67F2 | `LD A,#00` | [PresentInterlacedFrame.asm](../Source/Intro/PresentInterlacedFrame.asm) |
| Intro | #67FF | #6839 | `NOP` | [PresentInterlacedFrame.asm](../Source/Intro/PresentInterlacedFrame.asm) |
| Intro | #6827 | #6831 | `LD SP,#3131` | [ScatterTextureToScreen.asm](../Source/Intro/ScatterTextureToScreen.asm) |
| Intro | #682A | #68A1 | `LD SP,#3131` | [ScatterTextureToScreen.asm](../Source/Intro/ScatterTextureToScreen.asm) |
| Intro | #6835 | #6831 | `LD SP,#3131` | [ScatterTextureToScreen.asm](../Source/Intro/ScatterTextureToScreen.asm) |
| Intro | #68A4 | #692A | `LD SP,#3131` | [RunAttributeWriter.asm](../Source/Intro/RunAttributeWriter.asm) |
| Intro | #6A2C | #6A47 | `LD SP,#3131` | [AdvanceParameters.asm](../Source/Intro/AdvanceParameters.asm) |
| Intro | #6A4B | #6A5E | `CALL #CDCD` | [RunTimedEffect.asm](../Source/Intro/RunTimedEffect.asm) |
| Intro | #6B12 | #67FE | `LD H,#14` | [InitializeColumnEffect.asm](../Source/Intro/InitializeColumnEffect.asm) |
| Intro | #6BB4 | #6BBD | `LD SP,#3131` | [RenderLookupTexture.asm](../Source/Intro/RenderLookupTexture.asm) |
| Intro | #6BE3 | #6BF3 | `LD SP,#3131` | [RunTextureSampler.asm](../Source/Intro/RunTextureSampler.asm) |
| Intro | #6BFC | #6BA2 | `LD HL,#9400` | [AdvanceTexturePhases.asm](../Source/Intro/AdvanceTexturePhases.asm) |
| Intro | #6C05 | #6BA6 | `LD BC,#9500` | [AdvanceTexturePhases.asm](../Source/Intro/AdvanceTexturePhases.asm) |
| Intro | #6C0E | #6BA9 | `LD HL,#9600` | [AdvanceTexturePhases.asm](../Source/Intro/AdvanceTexturePhases.asm) |
| Intro | #6C17 | #6C12 | `LD HL,#6400` | [AdvanceTexturePhases.asm](../Source/Intro/AdvanceTexturePhases.asm) |
| Intro | #6C1D | #6BAC | `LD DE,#9700` | [AdvanceTexturePhases.asm](../Source/Intro/AdvanceTexturePhases.asm) |
| Intro | #6C27 | #6C22 | `LD A,#A1` | [AdvanceTextureScale.asm](../Source/Intro/AdvanceTextureScale.asm) |
| Intro | #6C35 | #6C2E | `LD A,#00` | [AdvanceTextureScale.asm](../Source/Intro/AdvanceTextureScale.asm) |
| Intro | #6C46 | #6C3F | `LD A,#00` | [AdvanceTextureScale.asm](../Source/Intro/AdvanceTextureScale.asm) |
| Intro | #6C5E | #6BB2 | `LD HL,#2121` | [SelectTexturePointerRow.asm](../Source/Intro/SelectTexturePointerRow.asm) |
| Intro | #6D43 | #6D40 | `LD A,#80` | [InitializeLookupEffect.asm](../Source/Intro/InitializeLookupEffect.asm) |
| Intro | #6DB9 | #6BDA | `CALL #6BE3` | [BuildMirroredTexture.asm](../Source/Intro/BuildMirroredTexture.asm) |
| Intro | #6DC2 | #6BA2 | `LD HL,#9400` | [BuildMirroredTexture.asm](../Source/Intro/BuildMirroredTexture.asm) |
| Intro | #6DC5 | #6BA6 | `LD BC,#9500` | [BuildMirroredTexture.asm](../Source/Intro/BuildMirroredTexture.asm) |
| Intro | #6DC8 | #6BA9 | `LD HL,#9600` | [BuildMirroredTexture.asm](../Source/Intro/BuildMirroredTexture.asm) |
| Intro | #6DCB | #6BAC | `LD DE,#9700` | [BuildMirroredTexture.asm](../Source/Intro/BuildMirroredTexture.asm) |
| StationBoot | #41E6 | #6307 | `LD BC,#02FF` | [StartStation.asm](../Source/StationBoot/StartStation.asm) |
| StationBoot | #428C | #6304 | `LD DE,#5801` | [StartStation.asm](../Source/StationBoot/StartStation.asm) |
| StationBoot | #42AC | #6309 | `LD (HL),L` | [StartStation.asm](../Source/StationBoot/StartStation.asm) |
| Station | #63CB | #9B16 | `LD A,#00` | [SuspendPointer.asm](../Source/Station/SuspendPointer.asm) |
| Station | #63E0 | #9B16 | `LD A,#00` | [ResumePointer.asm](../Source/Station/ResumePointer.asm) |
| Station | #63E7 | #9B16 | `LD A,#00` | [ResumePointer.asm](../Source/Station/ResumePointer.asm) |
| Station | #6465 | #64B3 | `LD DE,#0000` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #648B | #9A8D | `LD IX,#0000` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #648F | #9A90 | `CALL #9A58` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #6496 | #64B3 | `LD DE,#0000` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #64C2 | #6550 | `LD DE,#0000` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #64DA | #6501 | `LD B,#08` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #64FD | #6548 | `LD A,#00` | [DrawPointer.asm](../Source/Station/DrawPointer.asm) |
| Station | #654C | #6548 | `LD A,#00` | [RestorePointer.asm](../Source/Station/RestorePointer.asm) |
| Station | #6597 | #65D1 | `RL (IX+#05)` | [ConfigureMouseButtons.asm](../Source/Station/ConfigureMouseButtons.asm) |
| Station | #659C | #65CC | `RL (IX+#00)` | [ConfigureMouseButtons.asm](../Source/Station/ConfigureMouseButtons.asm) |
| Station | #65A2 | #65C7 | `JR #658E` | [ConfigureMouseButtons.asm](../Source/Station/ConfigureMouseButtons.asm) |
| Station | #6783 | #9A89 | `CALL #9A58` | [UpdateBodyMotion.asm](../Source/Station/DropShipDetailPanels.asm) |
| Station | #67DC | #67D7 | `LD A,#FF` | [UpdateShipListHover.asm](../Source/Station/UpdateShipListHover.asm) |
| Station | #67E7 | #BD26 | `LD A,#00` | [DrawModelListPanel.asm](../Source/Station/DrawModelListPanel.asm) |
| Station | #67EC | #67D7 | `LD A,#FF` | [DrawModelListPanel.asm](../Source/Station/DrawModelListPanel.asm) |
| Station | #67F1 | #BD73 | `LD A,#00` | [DrawModelListPanel.asm](../Source/Station/DrawModelListPanel.asm) |
| Station | #6833 | #67D2 | `LD DE,#1E1B` | [DrawModelListPanel.asm](../Source/Station/DrawModelListPanel.asm) |
| Station | #6891 | #9A89 | `CALL #9A58` | [DrawShipPreview.asm](../Source/Station/DrawShipPreview.asm) |
| Station | #69BA | #BD26 | `LD A,#00` | [Unknown69B8.asm](../Source/Station/IndexHelpText.asm) |
| Station | #6A57 | #6A52 | `LD A,#FF` | [UpdateIndexListHover.asm](../Source/Station/UpdateIndexListHover.asm) |
| Station | #6A63 | #6A52 | `LD A,#FF` | [DrawItem22.asm](../Source/Station/DrawHelpContents.asm) |
| Station | #6A7A | #6A4D | `LD DE,#1E0B` | [DrawItem22.asm](../Source/Station/DrawHelpContents.asm) |
| Station | #6A7F | #BD26 | `LD A,#00` | [Unknown6A7E.asm](../Source/Station/DisableTextWrap.asm) |
| Station | #6AC8 | #BD26 | `LD A,#00` | [Unknown6AC6.asm](../Source/Station/UpdateEquipmentInfo.asm) |
| Station | #6AD3 | #6AE0 | `LD HL,#0000` | [Unknown6AC6.asm](../Source/Station/UpdateEquipmentInfo.asm) |
| Station | #6B9A | #6B95 | `LD A,#FF` | [UpdateEnvironmentHover.asm](../Source/Station/UpdateEnvironmentHover.asm) |
| Station | #6BAD | #6B95 | `LD A,#FF` | [DrawItem41.asm](../Source/Station/DrawEnvironmentPanel.asm) |
| Station | #6BBA | #6B90 | `LD DE,#1E0B` | [DrawItem41.asm](../Source/Station/DrawEnvironmentPanel.asm) |
| Station | #6C01 | #BD26 | `LD A,#00` | [Unknown6C00.asm](../Source/Station/SetupEnvironmentText.asm) |
| Station | #6C06 | #BD73 | `LD A,#00` | [Unknown6C00.asm](../Source/Station/SetupEnvironmentText.asm) |
| Station | #6DA1 | #6D75 | `LD A,#00` | [DrawMapPanelContents.asm](../Source/Station/DrawMapPanelContents.asm) |
| Station | #6DA4 | #6D90 | `LD A,#00` | [DrawMapPanelContents.asm](../Source/Station/DrawMapPanelContents.asm) |
| Station | #6DB6 | #6D7B | `LD A,#00` | [DrawMapPanel.asm](../Source/Station/DrawMapPanel.asm) |
| Station | #6DB9 | #6D75 | `LD A,#00` | [DrawMapPanel.asm](../Source/Station/DrawMapPanel.asm) |
| Station | #6DBC | #6D90 | `LD A,#00` | [DrawMapPanel.asm](../Source/Station/DrawMapPanel.asm) |
| Station | #6DDC | #BD26 | `LD A,#00` | [DrawDecodedMessagePanel.asm](../Source/Station/DrawDecodedMessagePanel.asm) |
| Station | #6F59 | #6F54 | `LD A,#FF` | [UpdateMissionRowHover.asm](../Source/Station/UpdateMissionRowHover.asm) |
| Station | #6FCD | #6F54 | `LD A,#FF` | [DrawItem31.asm](../Source/Station/DrawItem31.asm) |
| Station | #6FD1 | #BD26 | `LD A,#00` | [DrawItem31.asm](../Source/Station/DrawItem31.asm) |
| Station | #706D | #7068 | `LD A,#FF` | [RunTradeEventAndRedraw.asm](../Source/Station/RunTradeEventAndRedraw.asm) |
| Station | #707C | #7068 | `LD A,#FF` | [DrawTradePanel.asm](../Source/Station/DrawTradePanel.asm) |
| Station | #7092 | #7063 | `LD DE,#1E23` | [DrawTradePanel.asm](../Source/Station/DrawTradePanel.asm) |
| Station | #7155 | #BD26 | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #715A | #BD73 | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #715F | #BD7E | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #7164 | #BD89 | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #7169 | #BD94 | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #716E | #BD9F | `LD A,#00` | [SetMarketTextColumns.asm](../Source/Station/SetMarketTextColumns.asm) |
| Station | #721C | #7217 | `LD A,#FF` | [UpdateEquipmentHover.asm](../Source/Station/UpdateEquipmentHover.asm) |
| Station | #722F | #7217 | `LD A,#FF` | [DrawItem38.asm](../Source/Station/DrawEquipmentList.asm) |
| Station | #7248 | #7212 | `LD DE,#1E1B` | [DrawItem38.asm](../Source/Station/DrawEquipmentList.asm) |
| Station | #728C | #7306 | `LD A,#00` | [Unknown724C.asm](../Source/Station/PrintEquipmentRows.asm) |
| Station | #7340 | #BD26 | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #7345 | #BD73 | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #734A | #BD7E | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #734F | #BD89 | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #7354 | #BD94 | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #735B | #72DD | `LD A,#00` | [Unknown733F.asm](../Source/Station/SetupEquipmentColumns.asm) |
| Station | #748E | #7489 | `LD A,#FF` | [UpdateToPositionHover.asm](../Source/Station/UpdateToPositionHover.asm) |
| Station | #749A | #7489 | `LD A,#FF` | [DrawItem43.asm](../Source/Station/DrawSaveSlotPanel.asm) |
| Station | #749E | #BD26 | `LD A,#00` | [DrawItem43.asm](../Source/Station/DrawSaveSlotPanel.asm) |
| Station | #7517 | #7512 | `LD A,#FF` | [UpdateFromPositionHover.asm](../Source/Station/UpdateFromPositionHover.asm) |
| Station | #7523 | #7512 | `LD A,#FF` | [DrawItem44.asm](../Source/Station/DrawLoadSlotPanel.asm) |
| Station | #7527 | #BD26 | `LD A,#00` | [DrawItem44.asm](../Source/Station/DrawLoadSlotPanel.asm) |
| Station | #757F | #757A | `LD A,#FF` | [HoverContextMenu.asm](../Source/Station/HoverContextMenu.asm) |
| Station | #758B | #757A | `LD A,#FF` | [DrawItem40.asm](../Source/Station/DrawItem40.asm) |
| Station | #7590 | #BD26 | `LD A,#00` | [DrawItem40.asm](../Source/Station/DrawItem40.asm) |
| Station | #762C | #7627 | `LD A,#FF` | [UpdateGameSettingsHover.asm](../Source/Station/UpdateGameSettingsHover.asm) |
| Station | #763F | #7627 | `LD A,#FF` | [DrawItem42.asm](../Source/Station/DrawGameSettings.asm) |
| Station | #764C | #7622 | `LD DE,#1E0B` | [DrawItem42.asm](../Source/Station/DrawGameSettings.asm) |
| Station | #766D | #BD26 | `LD A,#00` | [Unknown766C.asm](../Source/Station/SetupGameSettingsText.asm) |
| Station | #7672 | #BD73 | `LD A,#00` | [Unknown766C.asm](../Source/Station/SetupGameSettingsText.asm) |
| Station | #7696 | #BD26 | `LD A,#00` | [DrawSystemInfoPanel.asm](../Source/Station/DrawSystemInfoPanel.asm) |
| Station | #78A6 | #9A89 | `CALL #9A58` | [DrawVariantPanel.asm](../Source/Station/DrawVariantPanel.asm) |
| Station | #795D | #BD26 | `LD A,#00` | [DrawItem45.asm](../Source/Station/DrawWelcomePanel.asm) |
| Station | #7A11 | #9E78 | `LD A,#00` | [Unknown79C7.asm](../Source/Station/ConfirmShipModelTrade.asm) |
| Station | #7A4E | #79DD | `LD A,#00` | [Unknown7A24.asm](../Source/Station/SelectSaleMode.asm) |
| Station | #7A79 | #79DD | `LD A,#00` | [Unknown7A64.asm](../Source/Station/SelectPurchaseMode.asm) |
| Station | #7CA9 | #7C99 | `LD HL,#990A` | [CycleStoredMapPoint.asm](../Source/Station/CycleStoredMapPoint.asm) |
| Station | #7CDB | #7CCC | `LD HL,#99A3` | [Unknown7CC6.asm](../Source/Station/CenterContractMap.asm) |
| Station | #7D73 | #7068 | `LD A,#FF` | [SellCurrentCargo.asm](../Source/Station/SellCurrentCargo.asm) |
| Station | #7DC6 | #6ACC | `LD A,#00` | [OpenEquipmentPanels.asm](../Source/Station/OpenEquipmentPanels.asm) |
| Station | #7E29 | #67D7 | `LD A,#FF` | [ResetShipPanelSelection.asm](../Source/Station/ResetShipPanelSelection.asm) |
| Station | #7E2D | #79DD | `LD A,#00` | [ResetShipPanelSelection.asm](../Source/Station/ResetShipPanelSelection.asm) |
| Station | #7F3A | #BD26 | `LD A,#00` | [DrawItem00.asm](../Source/Station/DrawItem00.asm) |
| Station | #9A5A | #9AB7 | `LD A,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9A5D | #9A99 | `LD A,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9A62 | #A9A9 | `AND #80` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9A69 | #A9A9 | `AND #80` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9A95 | #9A90 | `CALL #9A58` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9A9E | #9A99 | `LD A,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9AA1 | #9A82 | `LD A,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9ABC | #9AB7 | `LD A,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9AD2 | #9AD0 | `LD D,#00` | [MainLoop.asm](../Source/Station/MainLoop.asm) |
| Station | #9AEB | #9C0D | `LD SP,#0000` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B29 | #9B62 | `CP #00` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B37 | #9B72 | `LD A,#00` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B63 | #9B62 | `CP #00` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B80 | #9B7E | `LD A,#32` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B87 | #9B7E | `LD A,#32` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9B98 | #9A99 | `LD A,#00` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9BC1 | #9C0D | `LD SP,#0000` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9BC4 | #9C11 | `JP #0000` | [Interrupt.asm](../Source/Station/Interrupt.asm) |
| Station | #9C91 | #9D48 | `LD C,#00` | [RebuildInterface.asm](../Source/Station/RebuildInterface.asm) |
| Station | #9C96 | #9A82 | `LD A,#00` | [RebuildInterface.asm](../Source/Station/RebuildInterface.asm) |
| Station | #9DC1 | #9E31 | `LD HL,#FFF0` | [DispatchInterfaceEvent.asm](../Source/Station/DispatchInterfaceEvent.asm) |
| Station | #9DDC | #9E31 | `LD HL,#FFF0` | [DispatchInterfaceEvent.asm](../Source/Station/DispatchInterfaceEvent.asm) |
| Station | #9DF8 | #CA20 | `LD A,#00` | [DispatchInterfaceEvent.asm](../Source/Station/DispatchInterfaceEvent.asm) |
| Station | #9E13 | #9CAA | `LD A,#00` | [DispatchInterfaceEvent.asm](../Source/Station/DispatchInterfaceEvent.asm) |
| Station | #9E16 | #9A82 | `LD A,#00` | [DispatchInterfaceEvent.asm](../Source/Station/DispatchInterfaceEvent.asm) |
| Station | #9E87 | #9E78 | `LD A,#00` | [CloseActiveItem.asm](../Source/Station/CloseActiveItem.asm) |
| Station | #9E90 | #9E8B | `CALL #9A58` | [CloseActiveItem.asm](../Source/Station/CloseActiveItem.asm) |
| Station | #A098 | #A0A3 | `LD A,#FF` | [FillWindowBody.asm](../Source/Station/FillWindowBody.asm) |
| Station | #A09B | #A0C1 | `LD SP,#0000` | [FillWindowBody.asm](../Source/Station/FillWindowBody.asm) |
| Station | #A383 | #A397 | `LD A,#0A` | [SkipCrRecords.asm](../Source/Station/SkipCrRecords.asm) |
| Station | #A38C | #A397 | `LD A,#0A` | [SkipCrRecords.asm](../Source/Station/SkipCrRecords.asm) |
| Station | #A402 | #A437 | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A408 | #A43C | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A40E | #A441 | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A414 | #A446 | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A41A | #A44B | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A420 | #A450 | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A426 | #A45A | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A42C | #A45F | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A432 | #A455 | `LD A,#00` | [SaveTextWindow.asm](../Source/Station/SaveTextWindow.asm) |
| Station | #A438 | #AEBB | `LD A,#00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A43D | #AEC7 | `LD A,#00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A442 | #AEBF | `LD A,#00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A447 | #AECB | `LD A,#00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A44C | #AEB3 | `CP #00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A451 | #AEAB | `CP #00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A456 | #BD26 | `LD A,#00` | [RestoreTextWindow.asm](../Source/Station/RestoreTextWindow.asm) |
| Station | #A4A4 | #9B16 | `LD A,#00` | [BeginScreenUpdate.asm](../Source/Station/BeginScreenUpdate.asm) |
| Station | #A6F3 | #BD26 | `LD A,#00` | [DrawItem01.asm](../Source/Station/DrawItem01.asm) |
| Station | #A773 | #9A89 | `CALL #9A58` | [HideAllItems.asm](../Source/Station/HideAllItems.asm) |
| Station | #A778 | #9CAA | `LD A,#00` | [HideAllItems.asm](../Source/Station/HideAllItems.asm) |
| Station | #A784 | #9A89 | `CALL #9A58` | [CloseAllItems.asm](../Source/Station/CloseAllItems.asm) |
| Station | #A925 | #A999 | `LD A,#00` | [GenerateMarket.asm](../Source/Station/GenerateMarket.asm) |
| Station | #A929 | #A967 | `LD A,#00` | [GenerateMarket.asm](../Source/Station/GenerateMarket.asm) |
| Station | #AD3D | #AED5 | `LD L,B` | [SkipJustifyRow.asm](../Source/Station/SkipJustifyRow.asm) |
| Station | #AD43 | #AED6 | `LD C,B` | [SkipJustifyRow.asm](../Source/Station/SkipJustifyRow.asm) |
| Station | #AD4A | #AD4E | `LD C,#00` | [SkipJustifyRow.asm](../Source/Station/SkipJustifyRow.asm) |
| Station | #AD9C | #AED5 | `LD L,B` | [SkipJustifyRow.asm](../Source/Station/SkipJustifyRow.asm) |
| Station | #ADA2 | #AED6 | `LD C,B` | [SkipJustifyRow.asm](../Source/Station/SkipJustifyRow.asm) |
| Station | #ADD6 | #ADDA | `LD C,#00` | [PrintJustified.asm](../Source/Station/PrintJustified.asm) |
| Station | #AF04 | #AF0A | `JP #0000` | [DrawGlyph.asm](../Source/Station/DrawGlyph.asm) |
| Station | #BF00 | #BF08 | `JR #BF09` | [RegisterItemCells.asm](../Source/Station/RegisterItemCells.asm) |
| Station | #BF51 | #C17C | `LD (HL),D` | [PrepareFrameRaster.asm](../Source/Station/PrepareFrameRaster.asm) |
| Station | #BF56 | #C1BC | `LD (HL),C` | [PrepareFrameRaster.asm](../Source/Station/PrepareFrameRaster.asm) |
| Station | #BF67 | #C17C | `LD (HL),D` | [PrepareFrameRaster.asm](../Source/Station/PrepareFrameRaster.asm) |
| Station | #BF6A | #C17D | `INC L` | [PrepareFrameRaster.asm](../Source/Station/PrepareFrameRaster.asm) |
| Station | #BF83 | #C1BC | `LD (HL),C` | [PrepareFrameRaster.asm](../Source/Station/PrepareFrameRaster.asm) |
| Station | #C052 | #AEBB | `LD A,#00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C056 | #AEBF | `LD A,#00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C06D | #AEC7 | `LD A,#00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C071 | #AECB | `LD A,#00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C078 | #AEB3 | `CP #00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C07F | #AEAB | `CP #00` | [SetupTextWindow.asm](../Source/Station/SetupTextWindow.asm) |
| Station | #C09C | #C0CA | `CALL #C1C0` | [DrawBandFrame.asm](../Source/Station/DrawBandFrame.asm) |
| Station | #C0AB | #C17F | `JR #C180` | [DrawBandFrame.asm](../Source/Station/DrawBandFrame.asm) |
| Station | #C24F | #AEBB | `LD A,#00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C253 | #AEBF | `LD A,#00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C26C | #AEC7 | `LD A,#00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C270 | #AECB | `LD A,#00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C279 | #AEB3 | `CP #00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C282 | #AEAB | `CP #00` | [SetupInsetTextWindow.asm](../Source/Station/SetupInsetTextWindow.asm) |
| Station | #C2B0 | #BD26 | `LD A,#00` | [DrawCaptionItem.asm](../Source/Station/DrawCaptionItem.asm) |
| Station | #C2E5 | #BD26 | `LD A,#00` | [DrawCenteredItem.asm](../Source/Station/DrawCenteredItem.asm) |
| Station | #C30C | #BD4F | `JP #BD08` | [DrawCenteredItem.asm](../Source/Station/DrawCenteredItem.asm) |
| Station | #C343 | #BD4F | `JP #BD08` | [CenterItemLine.asm](../Source/Station/CenterItemLine.asm) |
| Station | #C366 | #AEBB | `LD A,#00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C36A | #AEBF | `LD A,#00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C383 | #AEC7 | `LD A,#00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C387 | #AECB | `LD A,#00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C390 | #AEB3 | `CP #00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C399 | #AEAB | `CP #00` | [SetupCenterText.asm](../Source/Station/SetupCenterText.asm) |
| Station | #C3B2 | #C17F | `JR #C180` | [DrawFrameType.asm](../Source/Station/DrawFrameType.asm) |
| Station | #C440 | #C17F | `JR #C180` | [DrawInsetFrame.asm](../Source/Station/DrawInsetFrame.asm) |
| Station | #C526 | #C5F5 | `LD B,#80` | [XorRectOutline.asm](../Source/Station/XorRectOutline.asm) |
| Station | #C536 | #C5F5 | `LD B,#80` | [XorRectOutline.asm](../Source/Station/XorRectOutline.asm) |
| Station | #C56C | #C570 | `JR #C571` | [XorOutlineRow.asm](../Source/Station/XorOutlineRow.asm) |
| Station | #C643 | #C658 | `JR #C659` | [FillRectangle.asm](../Source/Station/FillRectangle.asm) |
| Station | #C64F | #C656 | `LD A,#00` | [FillRectangle.asm](../Source/Station/FillRectangle.asm) |
| Station | #C878 | #9A82 | `LD A,#00` | [DropItemDraw.asm](../Source/Station/DropItemDraw.asm) |
| Station | #C887 | #C9BF | `CP #01` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C88A | #CADF | `CP #01` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C8C3 | #CAAC | `CP #03` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C8C6 | #CAB1 | `LD H,#03` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C8C9 | #CA77 | `CP #03` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C8CC | #CA7C | `LD L,#03` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C93D | #C9B1 | `LD BC,#0000` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #C941 | #C9B4 | `LD DE,#0000` | [TrackItemGeometry.asm](../Source/Station/TrackItemGeometry.asm) |
| Station | #CA05 | #9A82 | `LD A,#00` | [FinishGeometry.asm](../Source/Station/FinishGeometry.asm) |
| Station | #CA2C | #C9B1 | `LD BC,#0000` | [ResizeGeometry.asm](../Source/Station/ResizeGeometry.asm) |
| Station | #CA30 | #C9B4 | `LD DE,#0000` | [ResizeGeometry.asm](../Source/Station/ResizeGeometry.asm) |
| Station | #CBAA | #9A82 | `LD A,#00` | [RestoreItemBounds.asm](../Source/Station/RestoreItemBounds.asm) |
| Station | #CBE5 | #CC17 | `SCF` | [RepaintAndTrack.asm](../Source/Station/RepaintAndTrack.asm) |
| Station | #CBEE | #CC17 | `SCF` | [RepaintAndFlag.asm](../Source/Station/RepaintAndFlag.asm) |
| Station | #CC21 | #CCA4 | `LD HL,#0000` | [ActivateInterfaceCallback.asm](../Source/Station/ActivateInterfaceCallback.asm) |
| Station | #CC31 | #9A82 | `LD A,#00` | [ToggleItemBounds.asm](../Source/Station/ToggleItemBounds.asm) |
| Station | #CC8C | #9E8B | `CALL #9A58` | [ActivateItem.asm](../Source/Station/ActivateItem.asm) |
| Station | #CC94 | #9E78 | `LD A,#00` | [ActivateItem.asm](../Source/Station/ActivateItem.asm) |
| Station | #CC97 | #9E7E | `LD DE,#0000` | [ActivateItem.asm](../Source/Station/ActivateItem.asm) |
| Station | #CCA6 | #9E8B | `CALL #9A58` | [ActivateItem.asm](../Source/Station/ActivateItem.asm) |
| Station | #CCB8 | #C0F2 | `CALL #C1C0` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCBF | #C13E | `CALL #C1ED` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCC3 | #C0F8 | `CALL #C1ED` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCC7 | #C0FF | `CALL #C1C0` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCCB | #C144 | `CALL #C1C0` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCCF | #C095 | `LD HL,#C1C0` | [SetBandFillMode.asm](../Source/Station/SetBandFillMode.asm) |
| Station | #CCD7 | #C0FF | `CALL #C1C0` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Station | #CCDB | #C144 | `CALL #C1C0` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Station | #CCDF | #C095 | `LD HL,#C1C0` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Station | #CCE3 | #C0F2 | `CALL #C1C0` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Station | #CCEA | #C13E | `CALL #C1ED` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Station | #CCEE | #C0F8 | `CALL #C1ED` | [ResetBandMode.asm](../Source/Station/ResetBandMode.asm) |
| Text | #C004 | #C01C | `LD SP,#0000` | [RunMarketScript.asm](../Source/Text/RunMarketScript.asm) |
| Text | #C009 | #C028 | `LD A,#00` | [RunMarketScript.asm](../Source/Text/RunMarketScript.asm) |
| Text | #C0EE | #C028 | `LD A,#00` | [QueueTextAndStopAtLine.asm](../Source/Text/QueueTextAndStopAtLine.asm) |
| Text | #C4F4 | #C509 | `LD A,#00` | [CheckThresholdSet30.asm](../Source/Text/CheckThresholdSet30.asm) |
| Text | #C59B | #C509 | `LD A,#00` | [CheckThresholdSet14.asm](../Source/Text/CheckThresholdSet14.asm) |
| Text | #C689 | #C697 | `LD HL,#0000` | [PushCargo7BitWriter.asm](../Source/Text/PushCargo7BitWriter.asm) |
| Text | #C68C | #C69A | `LD A,#00` | [PushCargo7BitWriter.asm](../Source/Text/PushCargo7BitWriter.asm) |
| Text | #C6BF | #C6CD | `LD HL,#0000` | [PushEquipmentWeightWriter.asm](../Source/Text/PushEquipmentWeightWriter.asm) |
| Text | #C6C2 | #C6D0 | `LD A,#00` | [PushEquipmentWeightWriter.asm](../Source/Text/PushEquipmentWeightWriter.asm) |
| Text | #C7EE | #C804 | `JP #0000` | [ParseFieldSuffix.asm](../Source/Text/ParseFieldSuffix.asm) |
| Text | #C849 | #C856 | `LD B,#00` | [FindDelimitedRecord.asm](../Source/Text/FindDelimitedRecord.asm) |
| Text | #C84D | #C862 | `LD B,#00` | [FindDelimitedRecord.asm](../Source/Text/FindDelimitedRecord.asm) |
| Text | #C874 | #C884 | `LD HL,#0000` | [ComputeWeightedLoad.asm](../Source/Text/ComputeWeightedLoad.asm) |
| Text | #C8B7 | #C8BF | `ADD A,#00` | [ComputeWeightedLoad.asm](../Source/Text/ComputeWeightedLoad.asm) |
| Text | #C8D9 | #C8E1 | `ADD A,#00` | [ComputeWeightedLoad.asm](../Source/Text/ComputeWeightedLoad.asm) |
| Map | #C000 | #DFC4 | `LD A,#00` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C14C | #C22E | `LD SP,#0000` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C158 | #C18B | `CP #D0` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C15B | #C1E4 | `CP #D0` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C161 | #C211 | `CP #31` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C164 | #C1B6 | `CP #31` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C16A | #C174 | `LD BC,#8070` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C170 | #C1D1 | `LD BC,#8091` | [DrawMapScene.asm](../Source/Map/DrawMapScene.asm) |
| Map | #C782 | #C7B6 | `LD A,#00` | [PrepareVariantResources.asm](../Source/Map/PrepareVariantResources.asm) |
| Map | #C7E6 | #C817 | `LD A,#00` | [SelectVariantResource.asm](../Source/Map/SelectVariantResource.asm) |
| Map | #C90D | #C91D | `JR #C91E` | [XorSelectionBand.asm](../Source/Map/XorSelectionBand.asm) |
| Map | #D21F | #D306 | `ADD A,#00` | [DrawMapPointChain.asm](../Source/Map/DrawMapPointChain.asm) |
| Map | #D32E | #D338 | `NOP` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D334 | #D33B | `JR C,#D346` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D36D | #D377 | `NOP` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D373 | #D391 | `JR C,#D397` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D3AA | #D3B4 | `NOP` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D3B0 | #D3B7 | `JR C,#D3C2` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D3E9 | #D3F3 | `NOP` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #D3EF | #D40D | `JR C,#D413` | [RasterizeMapLine.asm](../Source/Map/RasterizeMapLine.asm) |
| Map | #DFCC | #E426 | `JR C,#E42B` | [DrawClippedMapArc.asm](../Source/Map/DrawClippedMapArc.asm) |
| Map | #DFCF | #E438 | `JR C,#E43E` | [DrawClippedMapArc.asm](../Source/Map/DrawClippedMapArc.asm) |
| Map | #DFD2 | #E44F | `JR C,#E454` | [DrawClippedMapArc.asm](../Source/Map/DrawClippedMapArc.asm) |
| Map | #DFD5 | #E460 | `JR C,#E466` | [DrawClippedMapArc.asm](../Source/Map/DrawClippedMapArc.asm) |
| Help | #DB57 | #DB01 | `LD A,#00` | [SelectText.asm](../Source/Help/SelectText.asm) |
| Music | #DB0B | #DB4D | `LD SP,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB0F | #DFAE | `LD BC,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB1A | #DF62 | `LD A,#03` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB1F | #DF98 | `LD HL,#E7C9` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB25 | #DF9F | `LD HL,#E7C9` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB2A | #DFA7 | `LD HL,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB43 | #E037 | `OR #00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB46 | #E136 | `OR #00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB49 | #E235 | `OR #00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB52 | #E078 | `LD SP,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB55 | #E178 | `LD SP,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB58 | #E276 | `LD SP,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB5B | #DE52 | `LD HL,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB5E | #DEE0 | `LD HL,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB61 | #E1F5 | `LD SP,#0000` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB64 | #DF89 | `LD DE,#DC10` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB69 | #DE5D | `LD A,#00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB6C | #DEEB | `LD A,#00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB6F | #E22B | `ADD A,#00` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB73 | #DFEF | `LD A,#FF` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB76 | #E1EE | `LD A,#FF` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB79 | #E0EE | `LD A,#FF` | [InitializeModule.asm](../Source/Music/InitializeModule.asm) |
| Music | #DB8E | #DF74 | `LD A,#00` | [ClearAyRegisters.asm](../Source/Music/ClearAyRegisters.asm) |
| Music | #DB9C | #DF6B | `JR #DF7F` | [ClearAyRegisters.asm](../Source/Music/ClearAyRegisters.asm) |
| Music | #DDD2 | #DE97 | `LD A,#00` | [SetGateTimingA.asm](../Source/Music/SetGateTimingA.asm) |
| Music | #DDD7 | #DE9F | `LD A,#00` | [SetGateTimingA.asm](../Source/Music/SetGateTimingA.asm) |
| Music | #DDDC | #DE90 | `JR #DEA3` | [SetGateTimingA.asm](../Source/Music/SetGateTimingA.asm) |
| Music | #DE12 | #E2E7 | `LD A,#00` | [SetGateTimingC.asm](../Source/Music/SetGateTimingC.asm) |
| Music | #DE15 | #E2D5 | `LD A,#00` | [SetGateTimingC.asm](../Source/Music/SetGateTimingC.asm) |
| Music | #DE1A | #E2E3 | `LD A,#00` | [SetGateTimingC.asm](../Source/Music/SetGateTimingC.asm) |
| Music | #DE25 | #DE1F | `JP #DFE3` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE2E | #E098 | `LD BC,#0000` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE33 | #DFFA | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE36 | #E03E | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE39 | #E055 | `ADD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE3C | #E07C | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE3F | #E09F | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE42 | #E0D7 | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE45 | #E06C | `LD HL,#0000` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE49 | #DFEF | `LD A,#FF` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE54 | #DFF6 | `LD SP,#0000` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE59 | #E011 | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE5E | #E02D | `ADD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE64 | #E07C | `LD A,#00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE6A | #E078 | `LD SP,#0000` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE6F | #E037 | `OR #00` | [TickDispatch.asm](../Source/Music/TickDispatch.asm) |
| Music | #DE93 | #DE90 | `JR #DEA3` | [UnknownDE90.asm](../Source/Music/StageGateAndSampleA.asm) |
| Music | #DE98 | #E0E9 | `LD A,#00` | [UnknownDE90.asm](../Source/Music/StageGateAndSampleA.asm) |
| Music | #DE9B | #E0D7 | `LD A,#00` | [UnknownDE90.asm](../Source/Music/StageGateAndSampleA.asm) |
| Music | #DEA0 | #E0E5 | `LD A,#00` | [UnknownDE90.asm](../Source/Music/StageGateAndSampleA.asm) |
| Music | #DEBC | #E198 | `LD BC,#0000` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEC1 | #E0F9 | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEC4 | #E13D | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEC7 | #E154 | `ADD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DECA | #E17C | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DECD | #E19F | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DED0 | #E1D7 | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DED3 | #E16C | `LD HL,#0000` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DED7 | #E0EE | `LD A,#FF` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEE2 | #E0F5 | `LD SP,#0000` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEE7 | #E110 | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEEC | #E12C | `ADD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEF2 | #E17C | `LD A,#00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEF8 | #E178 | `LD SP,#0000` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DEFD | #E136 | `OR #00` | [UnknownDEB9.asm](../Source/Music/StageChannelBRow.asm) |
| Music | #DF52 | #E2F1 | `LD HL,#0000` | [UnknownDF47.asm](../Source/Music/StageEnvelopeAndNoise.asm) |
| Music | #DF58 | #DF48 | `LD A,#00` | [UnknownDF47.asm](../Source/Music/StageEnvelopeAndNoise.asm) |
| Music | #DF5B | #E2EE | `LD DE,#0000` | [UnknownDF47.asm](../Source/Music/StageEnvelopeAndNoise.asm) |
| Music | #DF5E | #E2FA | `LD A,#00` | [UnknownDF47.asm](../Source/Music/StageEnvelopeAndNoise.asm) |
| Music | #DF63 | #E37D | `LD A,#03` | [UnknownDF47.asm](../Source/Music/StageEnvelopeAndNoise.asm) |
| Music | #DF70 | #E302 | `LD HL,#0000` | [UnknownDF70.asm](../Source/Music/CommitEnvelopeSlide.asm) |
| Music | #DF75 | #E2FA | `LD A,#00` | [UnknownDF70.asm](../Source/Music/CommitEnvelopeSlide.asm) |
| Music | #DF78 | #E309 | `LD A,#00` | [UnknownDF70.asm](../Source/Music/CommitEnvelopeSlide.asm) |
| Music | #DF7C | #DF6B | `JR #DF7F` | [UnknownDF70.asm](../Source/Music/CommitEnvelopeSlide.asm) |
| Music | #DF8F | #DF67 | `LD A,#00` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DF93 | #DFBD | `LD SP,#0000` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFA3 | #DF98 | `LD HL,#E7C9` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFB4 | #E393 | `LD DE,#0000` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFB9 | #E3C4 | `LD DE,#0000` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFC4 | #DF89 | `LD DE,#DC10` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFD3 | #DE2E | `LD (#E098),HL` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFD8 | #DE61 | `JR #DE72` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFDC | #DE31 | `JR #DE5C` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFE0 | #DE72 | `JR #DE90` | [AdvancePatternA.asm](../Source/Music/AdvancePatternA.asm) |
| Music | #DFEA | #E30E | `LD SP,#0000` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E001 | #DFFA | `LD A,#00` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E01F | #E011 | `LD A,#00` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E044 | #E03E | `LD A,#00` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E05A | #E055 | `ADD A,#00` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E073 | #E06C | `LD HL,#0000` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E083 | #E07C | `LD A,#00` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E0AB | #E098 | `LD BC,#0000` | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E0CF | #E09F | `LD A,#00` | [FinishChannelA.asm](../Source/Music/FinishChannelA.asm) |
| Music | #E0EA | #E0D7 | `LD A,#00` | [FinishChannelA.asm](../Source/Music/FinishChannelA.asm) |
| Music | #E100 | #E0F9 | `LD A,#00` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E11E | #E110 | `LD A,#00` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E143 | #E13D | `LD A,#00` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E159 | #E154 | `ADD A,#00` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E173 | #E16C | `LD HL,#0000` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E183 | #E17C | `LD A,#00` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E1AB | #E198 | `LD BC,#0000` | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E1CF | #E19F | `LD A,#00` | [FinishChannelB.asm](../Source/Music/FinishChannelB.asm) |
| Music | #E1EA | #E1D7 | `LD A,#00` | [FinishChannelB.asm](../Source/Music/FinishChannelB.asm) |
| Music | #E200 | #E1F9 | `LD A,#00` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E21D | #E20F | `LD A,#00` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E242 | #E23C | `LD A,#00` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E258 | #E253 | `ADD A,#00` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E271 | #E26A | `LD HL,#0000` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E281 | #E27A | `LD A,#00` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E2A9 | #E296 | `LD BC,#0000` | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E2CD | #E29D | `LD A,#00` | [FinishChannelC.asm](../Source/Music/FinishChannelC.asm) |
| Music | #E2E8 | #E2D5 | `LD A,#00` | [FinishChannelC.asm](../Source/Music/FinishChannelC.asm) |
| Music | #E305 | #E2EE | `LD DE,#0000` | [OutputAyFrame.asm](../Source/Music/OutputAyFrame.asm) |
| Music | #E30A | #E2FA | `LD A,#00` | [OutputAyFrame.asm](../Source/Music/OutputAyFrame.asm) |
| Music | #E341 | #DFE9 | `LD IX,#0000` | [OutputAyFrame.asm](../Source/Music/OutputAyFrame.asm) |
| Music | #E37F | #E37D | `LD A,#03` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E39A | #E393 | `LD DE,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3A9 | #DEBC | `LD (#E198),HL` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3AE | #DEEF | `JR #DF00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3B2 | #DEBF | `JR #DEEA` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3B6 | #DF00 | `JR #DF1E` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3BB | #DE1F | `JP #DFE3` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3CB | #E3C4 | `LD DE,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3D8 | #E296 | `LD BC,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3DC | #DE4D | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3EA | #DE5D | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3F1 | #DE48 | `CPL` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E3FE | #DFC9 | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E404 | #DF48 | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E409 | #DF51 | `LD HL,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E40E | #DF50 | `LD HL,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E413 | #DE6E | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E422 | #DE68 | `LD HL,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E427 | #DE6E | `LD A,#00` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E435 | #DE52 | `LD HL,#0000` | [UnknownE37C.asm](../Source/Music/AdvancePatternBC.asm) |
| Music | #E464 | #DF48 | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E469 | #DF51 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E46E | #DF50 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E480 | #DE68 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E489 | #DEDB | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E497 | #DEEB | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E49E | #DED6 | `CPL` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4AB | #E39F | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4B1 | #DF48 | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4B6 | #DF51 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4BB | #DF50 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4C0 | #DEFC | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4CF | #DEF6 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4D4 | #DEFC | `LD A,#00` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E4E2 | #DEE0 | `LD HL,#0000` | [UnknownE439.asm](../Source/Music/DecodePatternA.asm) |
| Music | #E511 | #DF67 | `LD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E518 | #DF48 | `LD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E51D | #DF51 | `LD HL,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E522 | #DF50 | `LD HL,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E534 | #DEF6 | `LD HL,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E543 | #E22B | `ADD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E548 | #E2D5 | `LD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E54C | #E1EE | `LD A,#FF` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E550 | #DF48 | `LD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E555 | #DF51 | `LD HL,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E55A | #DF50 | `LD HL,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E55F | #E235 | `OR #00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E56B | #E276 | `LD SP,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E570 | #E235 | `OR #00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E574 | #E27A | `LD A,#00` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E57F | #E1F5 | `LD SP,#0000` | [UnknownE4E6.asm](../Source/Music/DecodePatternB.asm) |
| Music | #E5B8 | #E3D0 | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5C0 | #DF48 | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5C5 | #DF51 | `LD HL,#0000` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5CA | #DF50 | `LD HL,#0000` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5DC | #E276 | `LD SP,#0000` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5E1 | #E27A | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5EC | #E1F9 | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5EF | #E23C | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5F2 | #E253 | `ADD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5F5 | #E27A | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5F8 | #E29D | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5FB | #E1EE | `LD A,#FF` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E5FE | #E2D5 | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E601 | #E26A | `LD HL,#0000` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E606 | #E20F | `LD A,#00` | [UnknownE583.asm](../Source/Music/DecodePatternC.asm) |
| Music | #E6B0 | #E29D | `LD A,#00` | [SetToneSlideC.asm](../Source/Music/SetToneSlideC.asm) |
| Music | #E6B3 | #E2CC | `LD A,#00` | [SetToneSlideC.asm](../Source/Music/SetToneSlideC.asm) |
| Music | #E6BC | #E2A6 | `LD HL,#0000` | [SetToneSlideC.asm](../Source/Music/SetToneSlideC.asm) |
| Music | #E6C1 | #E2AD | `JR #E2CB` | [SetToneSlideC.asm](../Source/Music/SetToneSlideC.asm) |
| Music | #E6C5 | #E2D5 | `LD A,#00` | [SetToneSlideC.asm](../Source/Music/SetToneSlideC.asm) |
| Action | #605F | #ECF6 | `LD HL,#0000` | [Unknown6040.asm](../Source/Action/QueueTextItemBank1.asm) |
| Action | #614C | #669F | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #614F | #666B | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #6152 | #664A | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #6155 | #668E | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #6158 | #667D | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #615B | #665C | `LD A,#00` | [RefreshFlightPanel.asm](../Source/Action/RefreshFlightPanel.asm) |
| Action | #6373 | #635C | `LD HL,#0000` | [ApplyPendingRecordLink.asm](../Source/Action/ApplyPendingRecordLink.asm) |
| Action | #6379 | #ECA9 | `LD HL,#0000` | [ApplyPendingRecordLink.asm](../Source/Action/ApplyPendingRecordLink.asm) |
| Action | #6658 | #664A | `LD A,#00` | [UpdatePanelGauges.asm](../Source/Action/UpdatePanelGauges.asm) |
| Action | #6679 | #666B | `LD A,#00` | [UpdatePanelGauges.asm](../Source/Action/UpdatePanelGauges.asm) |
| Action | #668A | #667D | `LD A,#00` | [UpdatePanelGauges.asm](../Source/Action/UpdatePanelGauges.asm) |
| Action | #669B | #668E | `LD A,#00` | [UpdatePanelGauges.asm](../Source/Action/UpdatePanelGauges.asm) |
| Action | #66A4 | #669F | `LD A,#00` | [UpdatePanelGauges.asm](../Source/Action/UpdatePanelGauges.asm) |
| Action | #673F | #7B6B | `CP #FD` | [SubtractScaledWorkVector.asm](../Source/Action/SubtractScaledWorkVector.asm) |
| Action | #6787 | #6781 | `LD HL,#8000` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #678F | #6781 | `LD HL,#8000` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #682E | #6682 | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6833 | #667D | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #683E | #683C | `LD A,#80` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6859 | #665C | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6865 | #667D | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6869 | #6682 | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6879 | #7B6B | `CP #FD` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #689F | #68D5 | `LD DE,#0000` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #68B2 | #68FD | `LD DE,#0000` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #68C5 | #6925 | `LD DE,#0000` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6962 | #6693 | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6967 | #668E | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6971 | #668E | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6975 | #6693 | `LD A,#00` | [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm) |
| Action | #6A89 | #AF48 | `LD DE,#0000` | [PrepareBodyTransform.asm](../Source/Action/PrepareBodyTransform.asm) |
| Action | #6A8F | #AF56 | `LD DE,#0000` | [PrepareBodyTransform.asm](../Source/Action/PrepareBodyTransform.asm) |
| Action | #6A95 | #AF69 | `LD DE,#0000` | [PrepareBodyTransform.asm](../Source/Action/PrepareBodyTransform.asm) |
| Action | #6C1C | #AF48 | `LD DE,#0000` | [TransformWorkComponents.asm](../Source/Action/TransformWorkComponents.asm) |
| Action | #6C22 | #AF56 | `LD DE,#0000` | [TransformWorkComponents.asm](../Source/Action/TransformWorkComponents.asm) |
| Action | #6C28 | #AF69 | `LD DE,#0000` | [TransformWorkComponents.asm](../Source/Action/TransformWorkComponents.asm) |
| Action | #6C97 | #AF48 | `LD DE,#0000` | [UpdateThirdGlyphVector.asm](../Source/Action/UpdateThirdGlyphVector.asm) |
| Action | #6C9D | #AF56 | `LD DE,#0000` | [UpdateThirdGlyphVector.asm](../Source/Action/UpdateThirdGlyphVector.asm) |
| Action | #6CA3 | #AF69 | `LD DE,#0000` | [UpdateThirdGlyphVector.asm](../Source/Action/UpdateThirdGlyphVector.asm) |
| Action | #6D42 | #6D39 | `LD A,#00` | [UpdateVisualEffects.asm](../Source/Action/UpdateVisualEffects.asm) |
| Action | #6D45 | #6D3D | `LD A,#00` | [UpdateVisualEffects.asm](../Source/Action/UpdateVisualEffects.asm) |
| Action | #6D61 | #AF69 | `LD DE,#0000` | [UpdateVisualEffects.asm](../Source/Action/UpdateVisualEffects.asm) |
| Action | #6D77 | #AF48 | `LD DE,#0000` | [UpdateVisualEffects.asm](../Source/Action/UpdateVisualEffects.asm) |
| Action | #6D8D | #AF56 | `LD DE,#0000` | [UpdateVisualEffects.asm](../Source/Action/UpdateVisualEffects.asm) |
| Action | #6E82 | #E5B3 | `LD DE,#0000` | [UpdateMotionFromControls.asm](../Source/Action/UpdateMotionFromControls.asm) |
| Action | #6E95 | #E5D2 | `LD DE,#0000` | [UpdateMotionFromControls.asm](../Source/Action/UpdateMotionFromControls.asm) |
| Action | #6EA8 | #E5ED | `LD DE,#0000` | [UpdateMotionFromControls.asm](../Source/Action/UpdateMotionFromControls.asm) |
| Action | #6EB0 | #669F | `LD A,#00` | [StepNearZeroWord.asm](../Source/Action/StepNearZeroWord.asm) |
| Action | #6EDA | #6EAD | `LD A,#00` | [StepNearZeroWord.asm](../Source/Action/StepNearZeroWord.asm) |
| Action | #6F5A | #6F59 | `LD C,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6F73 | #669F | `LD A,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6F77 | #6F56 | `LD A,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6F7F | #6F7B | `LD A,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6F8F | #6F8D | `LD A,#92` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6FB4 | #6FB0 | `LD A,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6FC4 | #6FC2 | `LD A,#92` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6FE9 | #6FE5 | `LD A,#00` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #6FF8 | #6FF6 | `LD A,#92` | [LatchControlsAndDecay.asm](../Source/Action/LatchControlsAndDecay.asm) |
| Action | #7876 | #792E | `LD (IY+#18),#10` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #792F | #792E | `LD (IY+#18),#10` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #794B | #799C | `LD DE,#0000` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #79A8 | #7B61 | `LD A,#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #79B4 | #7B61 | `LD A,#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #79C0 | #79DE | `ADD A,#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #79C9 | #7A6A | `LD (IX+#12),#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #7A25 | #6D39 | `LD A,#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #7A31 | #6D3D | `LD A,#00` | [SpawnAlternate.asm](../Source/Action/SpawnAlternate.asm) |
| Action | #7B5B | #7B59 | `LD A,#80` | [ScheduleSpawn.asm](../Source/Action/ScheduleSpawn.asm) |
| Action | #7C5F | #6D39 | `LD A,#00` | [ScheduleSpawn.asm](../Source/Action/ScheduleSpawn.asm) |
| Action | #7C6B | #6D3D | `LD A,#00` | [ScheduleSpawn.asm](../Source/Action/ScheduleSpawn.asm) |
| Action | #7EC3 | #7F0F | `LD DE,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #7EC7 | #7F12 | `LD HL,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #7ED6 | #7F23 | `LD DE,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #7EDA | #7F26 | `LD HL,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #7EE9 | #7F37 | `LD DE,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #7EED | #7F3A | `LD HL,#0000` | [StepRecordTowardWideVector.asm](../Source/Action/StepRecordTowardWideVector.asm) |
| Action | #A864 | #A85F | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A8AF | #664A | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A8B6 | #A8B3 | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A8C2 | #A8BC | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A8C5 | #666B | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A8FA | #ECA9 | `LD HL,#0000` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A925 | #664A | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A92F | #A92D | `LD A,#80` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A939 | #ECF6 | `LD HL,#0000` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A962 | #664A | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A969 | #A966 | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #A97B | #664A | `LD A,#00` | [UpdateFrame.asm](../Source/Action/UpdateFrame.asm) |
| Action | #AC4F | #ECA9 | `LD HL,#0000` | [ReadWordFromIX.asm](../Source/Action/ReadWordFromIX.asm) |
| Action | #AC52 | #ECF6 | `LD HL,#0000` | [ReadWordFromIX.asm](../Source/Action/ReadWordFromIX.asm) |
| Action | #AC61 | #F79C | `LD C,#0A` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC68 | #F798 | `LD C,#0A` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC6D | #A968 | `ADD A,#50` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC77 | #A8B5 | `ADD A,#14` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC7C | #7B6B | `CP #FD` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC7F | #6874 | `ADD A,#00` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC98 | #79A4 | `CP #F2` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AC9D | #7E07 | `OR #32` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #ACA2 | #7E09 | `LD H,#64` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #ACA7 | #7DE4 | `OR #20` | [ApplyParameterSet.asm](../Source/Action/ApplyParameterSet.asm) |
| Action | #AF10 | #AF14 | `JR NZ,#AF13` | [DivideScaledLogarithmic.asm](../Source/Action/DivideScaledLogarithmic.asm) |
| Action | #AF2B | #AF2F | `JR NZ,#AF2E` | [DivideScaledLogarithmic.asm](../Source/Action/DivideScaledLogarithmic.asm) |
| Action | #AF43 | #AFF1 | `LD IX,#0000` | [ComputePatchedVector.asm](../Source/Action/ComputePatchedVector.asm) |
| Action | #C9AC | #CB38 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9AF | #CC29 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9B4 | #CC25 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9B9 | #CB3C | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9BD | #CD22 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9C0 | #CB3A | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9C3 | #CC27 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9C6 | #CD26 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9CB | #CD24 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #C9F0 | #CD22 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CA0A | #CB38 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CA1D | #CC25 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CA55 | #CB3A | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CA66 | #CD24 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CA9E | #CC27 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CAD6 | #CB3C | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CAE7 | #CD26 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #CB1F | #CC29 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/Action/BuildRenderCoefficients.asm) |
| Action | #D10A | #D129 | `LD SP,#0000` | [ClearWorkBuffer.asm](../Source/Action/ClearWorkBuffer.asm) |
| Action | #E048 | #E021 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E04B | #ED83 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E065 | #CB3E | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E070 | #CB8B | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E07B | #CBD8 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E086 | #CB54 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E091 | #CBA1 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E09C | #CBEE | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E0A7 | #CB6F | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E0B2 | #CBBC | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E0BD | #CC09 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E0D7 | #E4A7 | `LD SP,#0000` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E101 | #AF48 | `LD DE,#0000` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E113 | #AF56 | `LD DE,#0000` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E125 | #AF69 | `LD DE,#0000` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E19D | #ED83 | `LD A,#00` | [RenderSceneFrame.asm](../Source/Action/RenderSceneFrame.asm) |
| Action | #E4B2 | #E4D6 | `LD SP,#0000` | [ReadRenderQueue.asm](../Source/Action/ReadRenderQueue.asm) |
| Action | #E55C | #E605 | `LD SP,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E56A | #E68C | `LD HL,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E571 | #E5B3 | `LD DE,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E577 | #E692 | `LD HL,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E57E | #E5D2 | `LD DE,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E584 | #E698 | `LD HL,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E58B | #E5ED | `LD DE,#0000` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E59A | #E59E | `JR #E59D` | [PrepareRecordScale.asm](../Source/Action/PrepareRecordScale.asm) |
| Action | #E63E | #E644 | `LD A,#00` | [UpdateRecordComponents.asm](../Source/Action/UpdateRecordComponents.asm) |
| Action | #E64B | #E644 | `LD A,#00` | [UpdateRecordComponents.asm](../Source/Action/UpdateRecordComponents.asm) |
| Action | #E68E | #E5B3 | `LD DE,#0000` | [RestoreHalvedOffsets.asm](../Source/Action/RestoreHalvedOffsets.asm) |
| Action | #E694 | #E5D2 | `LD DE,#0000` | [RestoreHalvedOffsets.asm](../Source/Action/RestoreHalvedOffsets.asm) |
| Action | #E69A | #E5ED | `LD DE,#0000` | [RestoreHalvedOffsets.asm](../Source/Action/RestoreHalvedOffsets.asm) |
| Action | #ECDD | #ECA9 | `LD HL,#0000` | [UpdateAyEffects.asm](../Source/Action/UpdateAyEffects.asm) |
| Action | #ECE4 | #ECAA | `LD HL,#0000` | [UpdateAyEffects.asm](../Source/Action/UpdateAyEffects.asm) |
| Action | #ED2E | #ECF6 | `LD HL,#0000` | [UpdateAyEffects.asm](../Source/Action/UpdateAyEffects.asm) |
| Action | #ED35 | #ECF7 | `LD HL,#0000` | [UpdateAyEffects.asm](../Source/Action/UpdateAyEffects.asm) |
| Action | #F575 | #E5B0 | `LD HL,#0000` | [ResetRecordUpdateBases.asm](../Source/Action/ResetRecordUpdateBases.asm) |
| Action | #F578 | #E5CF | `LD HL,#0000` | [ResetRecordUpdateBases.asm](../Source/Action/ResetRecordUpdateBases.asm) |
| Action | #F57B | #E5EA | `LD HL,#0000` | [ResetRecordUpdateBases.asm](../Source/Action/ResetRecordUpdateBases.asm) |
| Voxel | #E50A | #E7AF | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E510 | #E801 | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E516 | #E853 | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E51C | #E67B | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E522 | #E6CD | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E528 | #E71F | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E566 | #E7AF | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E58F | #E67B | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E5B8 | #E801 | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E5E1 | #E6CD | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E60A | #E853 | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E633 | #E71F | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E640 | #E7BA | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E646 | #E80C | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E64C | #E85E | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E6C5 | #E7BA | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E717 | #E80C | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E769 | #E85E | `LD HL,#0000` | [RotateBasisVectors.asm](../Source/Voxel/RotateBasisVectors.asm) |
| Voxel | #E8C1 | #E913 | `LD A,#00` | [SignedSeededProduct.asm](../Source/Voxel/SignedSeededProduct.asm) |
| Voxel | #EC06 | #EC5A | `LD (IY+#06),#00` | [CreateSmallEffect.asm](../Source/Voxel/CreateSmallEffect.asm) |
| Voxel | #EC0B | #EC7D | `LD (IY+#11),#00` | [CreateSmallEffect.asm](../Source/Voxel/CreateSmallEffect.asm) |
| Voxel | #EC10 | #EC79 | `LD (IY+#10),#00` | [ConfigureSmallEffect.asm](../Source/Voxel/ConfigureSmallEffect.asm) |
| Voxel | #EC15 | #EC6C | `LD A,#00` | [ConfigureSmallEffect.asm](../Source/Voxel/ConfigureSmallEffect.asm) |
| Voxel | #EC21 | #EC5A | `LD (IY+#06),#00` | [CreateLargeEffect.asm](../Source/Voxel/CreateLargeEffect.asm) |
| Voxel | #EC26 | #EC7D | `LD (IY+#11),#00` | [CreateLargeEffect.asm](../Source/Voxel/CreateLargeEffect.asm) |
| Voxel | #EC2B | #EC79 | `LD (IY+#10),#00` | [CreateLargeEffect.asm](../Source/Voxel/CreateLargeEffect.asm) |
| Voxel | #EC30 | #EC6C | `LD A,#00` | [CreateLargeEffect.asm](../Source/Voxel/CreateLargeEffect.asm) |
| Voxel | #EC86 | #ED7E | `LD A,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EC89 | #EC9D | `LD HL,#0000` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EC8C | #ECD2 | `LD HL,#0000` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #ECB3 | #ED7E | `LD A,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #ED23 | #EE17 | `LD A,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #ED30 | #EE4A | `JR NC,#EE53` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE53 | #EE78 | `JP #0000` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EDD3 | #F92A | `LD SP,#0000` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EDD7 | #F910 | `ADD A,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE13 | #F918 | `ADC A,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE27 | #F8B5 | `AND #0F` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE2A | #F8DB | `AND #0F` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE47 | #F921 | `LD HL,#0000` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE67 | #F905 | `SET 5,C` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #EE6B | #F907 | `LD H,#00` | [ClipSprite.asm](../Source/Voxel/ClipSprite.asm) |
| Voxel | #FA3E | #F9FA | `JR #F9F9` | [DrawProjectedEffect.asm](../Source/Voxel/DrawProjectedEffect.asm) |
| Voxel | #FA41 | #FA1D | `JR #FA1C` | [DrawProjectedEffect.asm](../Source/Voxel/DrawProjectedEffect.asm) |
| Voxel | #FA4A | #FA67 | `LD HL,#0000` | [DrawProjectedEffect.asm](../Source/Voxel/DrawProjectedEffect.asm) |
| Voxel | #FA4D | #FA6D | `LD BC,#0000` | [DrawProjectedEffect.asm](../Source/Voxel/DrawProjectedEffect.asm) |
| Voxel | #FA51 | #FA6A | `LD DE,#0000` | [DrawProjectedEffect.asm](../Source/Voxel/DrawProjectedEffect.asm) |
| ThreeD | #C9AC | #CB38 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9AF | #CC29 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9B4 | #CC25 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9B9 | #CB3C | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9BD | #CD22 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9C0 | #CB3A | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9C3 | #CC27 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9C6 | #CD26 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9CB | #CD24 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #C9F0 | #CD22 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CA0A | #CB38 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CA1D | #CC25 | `LD B,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CA55 | #CB3A | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CA66 | #CD24 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CA9E | #CC27 | `LD C,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CAD6 | #CB3C | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CAE7 | #CD26 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CB1F | #CC29 | `LD D,#00` | [BuildRenderCoefficients.asm](../Source/ThreeD/BuildRenderCoefficients.asm) |
| ThreeD | #CB87 | #D5FC | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CBD4 | #D62F | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CC21 | #D662 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CC77 | #D61E | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CCC7 | #D651 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CD17 | #D684 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CD6E | #D60D | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CDB8 | #D640 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE02 | #D673 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE09 | #D60D | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE0F | #D640 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE15 | #D673 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE1C | #D60D | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE22 | #D640 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE28 | #D673 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE3A | #D5FC | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE40 | #D62F | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE46 | #D662 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE4E | #D61E | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE56 | #D651 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE5E | #D684 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE65 | #D5FC | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE6B | #D62F | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE71 | #D662 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE77 | #D61E | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE7D | #D651 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE83 | #D684 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE8C | #D5FC | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE94 | #D62F | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CE9C | #D662 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEA2 | #D61E | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEA8 | #D651 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEAE | #D684 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEB7 | #D5FC | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEBF | #D62F | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEC7 | #D662 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CECF | #D61E | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CED7 | #D651 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #CEDF | #D684 | `LD A,#00` | [ComposeRenderMatrix.asm](../Source/ThreeD/ComposeRenderMatrix.asm) |
| ThreeD | #D10A | #D129 | `LD SP,#0000` | [ClearWorkBuffer.asm](../Source/ThreeD/ClearWorkBuffer.asm) |
| ThreeD | #D239 | #D244 | `JP #D100` | [PolygonFillRows.asm](../Source/ThreeD/PolygonFillRows.asm) |
| ThreeD | #D284 | #D275 | `LD HL,#0000` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D288 | #D217 | `ADD A,#00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D290 | #D4C4 | `LD E,#00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D2DF | #D213 | `SUB #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D2FC | #D213 | `SUB #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D31C | #D213 | `SUB #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D36B | #D213 | `SUB #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D38D | #D22A | `CP #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D392 | #D22C | `JR NC,#D263` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D399 | #D213 | `SUB #00` | [UpdatePolygonLeftEdge.asm](../Source/ThreeD/UpdatePolygonLeftEdge.asm) |
| ThreeD | #D3C2 | #D3B0 | `LD HL,#0000` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D3C6 | #D223 | `ADD A,#00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D3CF | #D387 | `LD L,#00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D41E | #D21F | `SUB #00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D43A | #D21F | `SUB #00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D459 | #D21F | `SUB #00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D4A6 | #D21F | `SUB #00` | [UpdatePolygonRightEdge.asm](../Source/ThreeD/UpdatePolygonRightEdge.asm) |
| ThreeD | #D4D0 | #D22A | `CP #00` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4D5 | #D22C | `JR NC,#D263` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4DF | #D22A | `CP #00` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4E4 | #D22C | `JR NC,#D263` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4EA | #D22A | `CP #00` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4EF | #D22C | `JR NC,#D263` | [SelectPolygonRowLimit.asm](../Source/ThreeD/SelectPolygonRowLimit.asm) |
| ThreeD | #D4F5 | #D21F | `SUB #00` | [SetShortNegativeRightStep.asm](../Source/ThreeD/SetShortNegativeRightStep.asm) |
| ThreeD | #D517 | #D3B7 | `CP #00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D537 | #D4C2 | `LD L,#00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D53B | #D4C4 | `LD E,#00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D53E | #D387 | `LD L,#00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D54C | #D275 | `LD HL,#0000` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D55C | #D3B0 | `LD HL,#0000` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D56A | #D1FF | `XOR #00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D56D | #D258 | `XOR #00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D5AA | #D264 | `LD SP,#0000` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D5BA | #D22A | `CP #00` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D5BF | #D22C | `JR NC,#D263` | [PreparePolygonFill.asm](../Source/ThreeD/PreparePolygonFill.asm) |
| ThreeD | #D5D5 | #D699 | `LD SP,#8E00` | [TransformObjectVertices.asm](../Source/ThreeD/TransformObjectVertices.asm) |
| ThreeD | #D5DB | #D7AC | `JR #D7AB` | [TransformObjectVertices.asm](../Source/ThreeD/TransformObjectVertices.asm) |
| ThreeD | #D5DE | #D7C7 | `JR #D7C6` | [TransformObjectVertices.asm](../Source/ThreeD/TransformObjectVertices.asm) |
| ThreeD | #D5E1 | #D9B9 | `JR #D9B8` | [TransformObjectVertices.asm](../Source/ThreeD/TransformObjectVertices.asm) |
| ThreeD | #D609 | #D69D | `LD BC,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D61A | #D6A0 | `LD DE,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D62B | #D6A3 | `LD HL,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D63C | #D69C | `LD BC,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D64D | #D69F | `LD DE,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D65E | #D6A2 | `LD HL,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D66F | #D6E2 | `LD DE,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D680 | #D6E1 | `LD DE,#0000` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D691 | #D6DF | `LD A,#00` | [PrepareRenderVertexProducts.asm](../Source/ThreeD/PrepareRenderVertexProducts.asm) |
| ThreeD | #D694 | #D79D | `LD SP,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6A6 | #D706 | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6B4 | #D73A | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6BA | #D747 | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6BE | #D756 | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6C9 | #D77B | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6CD | #D788 | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6D3 | #D761 | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6D9 | #D76E | `LD DE,#0000` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6F6 | #D77E | `LD A,#00` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6FA | #D78B | `LD A,#00` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D6FE | #D764 | `LD A,#00` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D702 | #D771 | `LD A,#00` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D799 | #D699 | `LD SP,#8E00` | [ProjectRenderVertexGroup.asm](../Source/ThreeD/ProjectRenderVertexGroup.asm) |
| ThreeD | #D7D0 | #D9C3 | `LD DE,#0000` | [ProjectRenderVertex.asm](../Source/ThreeD/ProjectRenderVertex.asm) |
| ThreeD | #DBE2 | #D560 | `LD A,#00` | [RenderClippedRecords.asm](../Source/ThreeD/RenderClippedRecords.asm) |
| ThreeD | #DC52 | #DE0F | `ADD A,#00` | [RenderClippedRecords.asm](../Source/ThreeD/RenderClippedRecords.asm) |
| ThreeD | #DD3E | #D560 | `LD A,#00` | [RenderInsideRecords.asm](../Source/ThreeD/RenderInsideRecords.asm) |
| ThreeD | #DDA0 | #DE0F | `ADD A,#00` | [RenderInsideRecords.asm](../Source/ThreeD/RenderInsideRecords.asm) |
| ThreeD | #DDFC | #DEED | `LD SP,#0000` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE35 | #DE3F | `NOP` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE3B | #DE42 | `JR C,#DE4F` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE68 | #DE72 | `NOP` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE6E | #DE7C | `JR C,#DE84` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE99 | #DEA3 | `NOP` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DE9F | #DEA6 | `JR C,#DEB3` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DECC | #DED6 | `NOP` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DED2 | #DEE0 | `JR C,#DEE8` | [DrawLinearLine.asm](../Source/ThreeD/DrawLinearLine.asm) |
| ThreeD | #DFCF | #DFE4 | `LD SP,#0000` | [CheckFaceOrientation.asm](../Source/ThreeD/CheckFaceOrientation.asm) |
| Controls | #C882 | #CA8A | `LD SP,#0000` | [UnknownC882.asm](../Source/Controls/CopyScreenRows.asm) |
| Controls | #C886 | #CA84 | `LD A,#00` | [UnknownC882.asm](../Source/Controls/CopyScreenRows.asm) |
| Controls | #CAAD | #CA8F | `LD BC,#0000` | [UnknownCA8D.asm](../Source/Controls/NextBufferRandom.asm) |
| Controls | #CC47 | #CE1E | `LD C,#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC50 | #CCD2 | `LD E,#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC55 | #CD9D | `LD E,#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC5D | #CC7E | `LD E,#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC60 | #CD49 | `LD E,#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC6F | #CD31 | `CALL #CE16` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CC72 | #CDFC | `CALL #CE16` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CD3F | #CE0B | `LD (HL),#00` | [UnknownCB00.asm](../Source/Controls/UpdateBufferPoints.asm) |
| Controls | #CE1A | #CE17 | `LD A,#00` | [UnknownCE16.asm](../Source/Controls/RespawnPointIndexPos.asm) |
| Controls | #CEAE | #CEB4 | `JR #CEB3` | [FillEvenSpan.asm](../Source/Controls/FillEvenSpan.asm) |
| Controls | #CEFA | #D240 | `LD IX,#0000` | [ProjectAndDrawBody.asm](../Source/Controls/ProjectAndDrawBody.asm) |
| Controls | #D58D | #D5B5 | `LD DE,#0020` | [PrepareInteriorSpan.asm](../Source/Controls/PrepareInteriorSpan.asm) |
| Controls | #D598 | #D5B5 | `LD DE,#0020` | [PrepareInteriorSpan.asm](../Source/Controls/PrepareInteriorSpan.asm) |
| Controls | #D59E | #D600 | `CP #00`, следующий байт также меняет JR | [PrepareInteriorSpan.asm](../Source/Controls/PrepareInteriorSpan.asm) |
| Controls | #D66B | #D672 | `LD A,#00` | [CircleRasterCore.asm](../Source/Controls/CircleRasterCore.asm) |
| Controls | #D6FE | #D705 | `LD A,#00` | [CircleRasterCore.asm](../Source/Controls/CircleRasterCore.asm) |
| Controls | #D70A | #D716 | `JR #D727` | [CircleRasterCore.asm](../Source/Controls/CircleRasterCore.asm) |
| Controls | #D76B | #D772 | `LD A,#00` | [ResumeCirclePushSpan.asm](../Source/Controls/ResumeCirclePushSpan.asm) |
| Controls | #D7F6 | #D7FD | `LD A,#00` | [ResumeCirclePushSpan.asm](../Source/Controls/ResumeCirclePushSpan.asm) |
| Controls | #D802 | #D80E | `JR #D80D` | [ResumeCirclePushSpan.asm](../Source/Controls/ResumeCirclePushSpan.asm) |
| Controls | #D865 | #D86C | `LD A,#00` | [RightClippedCircleCore.asm](../Source/Controls/RightClippedCircleCore.asm) |
| Controls | #D8E8 | #D8EF | `LD A,#00` | [RightClippedCircleCore.asm](../Source/Controls/RightClippedCircleCore.asm) |
| Controls | #D8F4 | #D900 | `JR #D8FF` | [RightClippedCircleCore.asm](../Source/Controls/RightClippedCircleCore.asm) |
| Controls | #DA7C | #DA83 | `LD A,#00` | [DrawSmallBody.asm](../Source/Controls/DrawSmallBody.asm) |
| Controls | #E021 | #E089 | `LD SP,#0000` | [UpdateGlyphIndicators.asm](../Source/Controls/UpdateGlyphIndicators.asm) |
| Controls | #E295 | #E48F | `LD SP,#0000` | [DrawRadar.asm](../Source/Controls/DrawRadar.asm) |
| Controls | #E2B2 | #E2B0 | `LD L,#00` | [DrawRadar.asm](../Source/Controls/DrawRadar.asm) |
| Controls | #E2C1 | #E2BC | `LD A,#00` | [DrawRadar.asm](../Source/Controls/DrawRadar.asm) |
| Controls | #E2C4 | #E471 | `LD A,#00` | [DrawRadar.asm](../Source/Controls/DrawRadar.asm) |
| Controls | #E47E | #E471 | `LD A,#00` | [DrawRadar.asm](../Source/Controls/DrawRadar.asm) |
| Controls | #EC11 | #ECA3 | `LD HL,#0000` | [UnknownEC0E.asm](../Source/Controls/InitializeTextWindow.asm) |
| Controls | #EC17 | #ECAA | `LD HL,#0000` | [UnknownEC0E.asm](../Source/Controls/InitializeTextWindow.asm) |
| Controls | #EC1C | #EC5D | `LD HL,#EC80` | [UnknownEC0E.asm](../Source/Controls/InitializeTextWindow.asm) |
| Controls | #EC7B | #EC5D | `LD HL,#EC80` | [UnknownEC59.asm](../Source/Controls/QueueTextItem.asm) |
| Controls | #ECAE | #ECAA | `LD HL,#0000` | [UnknownECA2.asm](../Source/Controls/ConsumeTextQueue.asm) |
| Controls | #ECC5 | #EFD6 | `LD C,#00` | [UnknownECA2.asm](../Source/Controls/ConsumeTextQueue.asm) |
| Controls | #ECD4 | #ECA3 | `LD HL,#0000` | [UnknownECA2.asm](../Source/Controls/ConsumeTextQueue.asm) |
| Controls | #ECE5 | #ECA3 | `LD HL,#0000` | [UnknownECA2.asm](../Source/Controls/ConsumeTextQueue.asm) |
| Controls | #ECEA | #EFD6 | `LD C,#00` | [UnknownECA2.asm](../Source/Controls/ConsumeTextQueue.asm) |
| Controls | #ED28 | #EFC1 | `LD SP,#0000` | [UnknownED28.asm](../Source/Controls/ScrollTextWindow.asm) |
| Controls | #EFEE | #EFD6 | `LD C,#00` | [UnknownEFC4.asm](../Source/Controls/PrintTextGlyph.asm) |
| Controls | #F110 | #F10E | `LD A,#80` | [UnknownF10D.asm](../Source/Controls/TickBcdCounter.asm) |
| Final | #60A3 | #6173 | `LD A,#00` | [InitializeFinal.asm](../Source/Final/InitializeFinal.asm) |
| Final | #60B3 | #6173 | `LD A,#00` | [InitializeFinal.asm](../Source/Final/InitializeFinal.asm) |
| Final | #6144 | #60D4 | `LD A,#01` | [ReadSpeedKeys.asm](../Source/Final/ReadSpeedKeys.asm) |
| Final | #61B8 | #6235 | `LD HL,#627D` | [PrepareFrame.asm](../Source/Final/PrepareFrame.asm) |
| Final | #61BE | #6238 | `LD BC,#0017` | [PrepareFrame.asm](../Source/Final/PrepareFrame.asm) |

| D3D | #EB10 | #EB7C | `JP #0000` | [MultiplyPreviewCoordinate.asm](../Source/D3D/MultiplyPreviewCoordinate.asm) |

| D3D | #EC3C | #D567 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC47 | #D599 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC52 | #D5CB | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC5D | #D574 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC68 | #D5A6 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC73 | #D5D8 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC7E | #D586 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC89 | #D5B8 | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EC94 | #D5EA | `LD A,#00` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ECA3 | #EEEF | `LD SP,#0000` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ECC6 | #EB7F | `LD DE,#0000` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ECD8 | #EB8D | `LD DE,#0000` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ECEA | #EBA0 | `LD DE,#0000` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ED4F | #ED5C | `JR #ED5B` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ED52 | #EDC4 | `JR #EDC3` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #ED55 | #EDFD | `JR #EDFC` | [BuildPreviewQueue.asm](../Source/D3D/BuildPreviewQueue.asm) |
| D3D | #EF6F | #D561 | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF72 | #D601 | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF77 | #D5FD | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF7C | #D565 | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF80 | #D6A9 | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF83 | #D563 | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF86 | #D5FF | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF89 | #D6AD | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EF8E | #D6AB | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EFB3 | #D6A9 | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EFC4 | #D561 | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EFCE | #D5FD | LD B,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EFEB | #D563 | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #EFF3 | #D6AB | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #F010 | #D5FF | LD C,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #F02D | #D565 | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #F035 | #D6AD | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #F052 | #D601 | LD D,#00 | [BuildPreviewModelMatrix.asm](../Source/D3D/BuildPreviewModelMatrix.asm) |
| D3D | #D595 | #D8C1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D5C7 | #D8D9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D5F9 | #D8F1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D634 | #D8D1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D669 | #D8E9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D69E | #D901 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D6DA | #D8C9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D709 | #D8E1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D738 | #D8F9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D73F | #D8C9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D745 | #D8E1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D74B | #D8F9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D752 | #D8C9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D758 | #D8E1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D75E | #D8F9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D770 | #D8C1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D776 | #D8D9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D77C | #D8F1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D784 | #D8D1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D78C | #D8E9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D794 | #D901 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D79B | #D8C1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7A1 | #D8D9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7A7 | #D8F1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7AD | #D8D1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7B3 | #D8E9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7B9 | #D901 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7C2 | #D8C1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7CA | #D8D9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7D2 | #D8F1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7D8 | #D8D1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7DE | #D8E9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7E4 | #D901 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7ED | #D8C1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7F5 | #D8D9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D7FD | #D8F1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D805 | #D8D1 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D80D | #D8E9 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #D815 | #D901 | LD A,#00 | [ComposePreviewMatrix.asm](../Source/D3D/ComposePreviewMatrix.asm) |
| D3D | #DBDF | #DA20 | JR #DA1F | [ConfigurePreviewProjectionScale.asm](../Source/D3D/ConfigurePreviewProjectionScale.asm) |
| D3D | #DBE2 | #DA3B | JR #DA3A | [ConfigurePreviewProjectionScale.asm](../Source/D3D/ConfigurePreviewProjectionScale.asm) |
| D3D | #DBE5 | #DAF9 | JR #DAF8 | [ConfigurePreviewProjectionScale.asm](../Source/D3D/ConfigurePreviewProjectionScale.asm) |
| D3D | #DBA8 | #DBB6 | LD HL,#0000 | [ProjectPreviewVertex.asm](../Source/D3D/ProjectPreviewVertex.asm) |
| D3D | #DBB2 | #DBC0 | LD (#0000),BC | [ProjectPreviewVertex.asm](../Source/D3D/ProjectPreviewVertex.asm) |
| D3D | #D908 | #DA11 | LD SP,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D91A | #D97A | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D928 | #D9AE | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D92E | #D9BB | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D932 | #D9CA | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D93D | #D9EF | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D941 | #D9FC | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D947 | #D9D5 | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D94D | #D9E2 | LD DE,#0000 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D96A | #D9F2 | LD A,#00 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D96E | #D9FF | LD A,#00 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D972 | #D9D8 | LD A,#00 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D976 | #D9E5 | LD A,#00 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #DA0D | #D90D | LD SP,#C600 | [ProjectPreviewVertexGroup.asm](../Source/D3D/ProjectPreviewVertexGroup.asm) |
| D3D | #D865 | #D911 | LD BC,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D86D | #D917 | LD HL,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D877 | #D956 | LD DE,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D87F | #D953 | LD A,#00 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D883 | #D913 | LD DE,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D887 | #D914 | LD DE,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D88A | #D910 | LD BC,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D88D | #D916 | LD HL,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D890 | #D955 | LD DE,#0000 | [ProjectPlanarVertexGroup.asm](../Source/D3D/ProjectPlanarVertexGroup.asm) |
| D3D | #D8C5 | #D911 | LD BC,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8CD | #D914 | LD DE,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8D5 | #D917 | LD HL,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8DD | #D910 | LD BC,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8E5 | #D913 | LD DE,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8ED | #D916 | LD HL,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8F5 | #D956 | LD DE,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D8FD | #D955 | LD DE,#0000 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D905 | #D953 | LD A,#00 | [PreparePreviewVertexProducts.asm](../Source/D3D/PreparePreviewVertexProducts.asm) |
| D3D | #D828 | #D861 | LD A,#00 | [ProjectPlanarModelGroups.asm](../Source/D3D/ProjectPlanarModelGroups.asm) |
| D3D | #D82B | #D87B | LD A,#00 | [ProjectPlanarModelGroups.asm](../Source/D3D/ProjectPlanarModelGroups.asm) |
| D3D | #D830 | #D869 | LD A,#00 | [ProjectPlanarModelGroups.asm](../Source/D3D/ProjectPlanarModelGroups.asm) |
| D3D | #D833 | #D871 | LD A,#00 | [ProjectPlanarModelGroups.asm](../Source/D3D/ProjectPlanarModelGroups.asm) |
| D3D | #D842 | #D90D | LD SP,#C600 | [ProjectPlanarModelGroups.asm](../Source/D3D/ProjectPlanarModelGroups.asm) |
| D3D | #D8A2 | #D90D | LD SP,#C600 | [ProjectPreviewModelGroups.asm](../Source/D3D/ProjectPreviewModelGroups.asm) |
| D3D | #DE5C | #DE66 | NOP | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DE62 | #DE69 | JR C,#DE74 | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DE9B | #DEA5 | NOP | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DEA1 | #DEBF | JR C,#DEC5 | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DED8 | #DEE2 | NOP | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DEDE | #DEE5 | JR C,#DEF0 | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DF17 | #DF21 | NOP | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #DF1D | #DF3B | JR C,#DF41 | [RasterizePreviewEdge.asm](../Source/D3D/RasterizePreviewEdge.asm) |
| D3D | #D247 | #D239 | LD A,#00 | [StepPreviewPolygonRow.asm](../Source/D3D/StepPreviewPolygonRow.asm) |
| D3D | #D2A0 | #D290 | LD HL,#0000 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D2A4 | #D227 | ADD A,#00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D2AD | #D23F | CP #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D2C7 | #D223 | SUB #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D2E4 | #D223 | SUB #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D304 | #D223 | SUB #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D31E | #D223 | SUB #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D33C | #D223 | SUB #00 | [UpdatePreviewLeftEdge.asm](../Source/D3D/UpdatePreviewLeftEdge.asm) |
| D3D | #D354 | #D239 | LD A,#00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D36A | #D358 | LD HL,#0000 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D36E | #D233 | ADD A,#00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D377 | #D243 | CP #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D391 | #D22F | SUB #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D3AD | #D22F | SUB #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D3CC | #D22F | SUB #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D3E3 | #D22F | SUB #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D401 | #D22F | SUB #00 | [UpdatePreviewRightEdge.asm](../Source/D3D/UpdatePreviewRightEdge.asm) |
| D3D | #D421 | #D35F | CP #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D442 | #D23B | CP #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D446 | #D23F | CP #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D449 | #D243 | CP #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D457 | #D290 | LD HL,#0000 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D467 | #D358 | LD HL,#0000 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D476 | #D20C | XOR #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D484 | #D257 | ADD A,#00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D4A2 | #D4C7 | OR #00 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #D4D5 | #D27E | LD SP,#0000 | [FillPreviewPolygon.asm](../Source/D3D/FillPreviewPolygon.asm) |
| D3D | #DDCC | #DE34 | ADD A,#00 | [RenderPreviewInsideFaces.asm](../Source/D3D/RenderPreviewInsideFaces.asm) |
| D3D | #DC7E | #DE34 | ADD A,#00 | [RenderPreviewClippedFaces.asm](../Source/D3D/RenderPreviewClippedFaces.asm) |
| D3D | #EF14 | #DAF6 | LD BC,#0000 | [RenderPreviewQueue.asm](../Source/D3D/RenderPreviewQueue.asm) |
| D3D | #EF1C | #DA38 | LD BC,#0000 | [RenderPreviewQueue.asm](../Source/D3D/RenderPreviewQueue.asm) |
| D3D | #EF24 | #DA16 | LD DE,#0000 | [RenderPreviewQueue.asm](../Source/D3D/RenderPreviewQueue.asm) |
| D3D | #EF2C | #EB8D | LD DE,#0000 | [RenderPreviewQueue.asm](../Source/D3D/RenderPreviewQueue.asm) |

| Station | #68D1 | #68EB | LD A,#00 | [RefreshShipPanels.asm](../Source/Station/RefreshShipPanels.asm) |

| Station | #67B9 | #E146 | D3D, банк 4, LD A,#00 | [ShipModelChoice.asm](../Source/Station/ShipModelChoice.asm) |

| Station | #67C4 | #6933 | Station, банк 5, LD HL,#0000 | [ShipModelChoice.asm](../Source/Station/ShipModelChoice.asm) |

| Station | #67CC | #68EB | Station, банк 5, LD A,#00 | [ShipModelChoice.asm](../Source/Station/ShipModelChoice.asm) |

| Station | #69CA | #6995 | Station, банк 5, LD HL,#0000 | [IndexHelpText.asm](../Source/Station/IndexHelpText.asm) |

| Station | #6991 | #A265 | Station, банк 2, CALL #0000 | [HandleHelpTextAction.asm](../Source/Station/HandleHelpTextAction.asm) |

| Station | #6997 | #A235 | Station, банк 2, LD DE,#0000 | [HandleHelpTextAction.asm](../Source/Station/HandleHelpTextAction.asm) |

| Station | #69A2 | #699D | Station, банк 5, LD HL,#0000 | [HandleHelpTextAction.asm](../Source/Station/HandleHelpTextAction.asm) |

| Station | #6A03 | #6A52 | Station, банк 5, LD A,#FF | [HandleHelpContentsAction.asm](../Source/Station/HandleHelpContentsAction.asm) |

| Station | #6A09 | #A265 | Station, банк 2, CALL #0000 | [HandleHelpContentsAction.asm](../Source/Station/HandleHelpContentsAction.asm) |

| Station | #6A0F | #A235 | Station, банк 2, LD DE,#0000 | [HandleHelpContentsAction.asm](../Source/Station/HandleHelpContentsAction.asm) |

| Station | #6A1A | #6A15 | Station, банк 5, LD HL,#0000 | [HandleHelpContentsAction.asm](../Source/Station/HandleHelpContentsAction.asm) |

| Station | #6A28 | #699D | Station, банк 5, LD HL,#0000 | [HandleHelpContentsAction.asm](../Source/Station/HandleHelpContentsAction.asm) |

| Station | #6A98 | #A265 | Station, банк 2, CALL #0000 | [HandleEquipmentInfoAction.asm](../Source/Station/HandleEquipmentInfoAction.asm) |

| Station | #6A9E | #A235 | Station, банк 2, LD DE,#0000 | [HandleEquipmentInfoAction.asm](../Source/Station/HandleEquipmentInfoAction.asm) |

| Station | #6AA9 | #6AA4 | Station, банк 5, LD HL,#0000 | [HandleEquipmentInfoAction.asm](../Source/Station/HandleEquipmentInfoAction.asm) |

| Station | #6AD9 | #6A9C | Station, банк 5, LD HL,#0000 | [UpdateEquipmentInfo.asm](../Source/Station/UpdateEquipmentInfo.asm) |

| Station | #6B11 | #6B95 | Station, банк 5, LD A,#FF | [HandleEnvironmentAction.asm](../Source/Station/HandleEnvironmentAction.asm) |

| Station | #6B17 | #A265 | Station, банк 2, CALL #0000 | [HandleEnvironmentAction.asm](../Source/Station/HandleEnvironmentAction.asm) |

| Station | #6B1D | #A235 | Station, банк 2, LD DE,#0000 | [HandleEnvironmentAction.asm](../Source/Station/HandleEnvironmentAction.asm) |

| Station | #6B28 | #6B23 | Station, банк 5, LD HL,#0000 | [HandleEnvironmentAction.asm](../Source/Station/HandleEnvironmentAction.asm) |

| Station | #75C1 | #7627 | Station, банк 5, LD A,#FF | [HandleGameSettingsAction.asm](../Source/Station/HandleGameSettingsAction.asm) |

| Station | #75C7 | #A265 | Station, банк 2, CALL #0000 | [HandleGameSettingsAction.asm](../Source/Station/HandleGameSettingsAction.asm) |

| Station | #75CD | #A235 | Station, банк 2, LD DE,#0000 | [HandleGameSettingsAction.asm](../Source/Station/HandleGameSettingsAction.asm) |

| Station | #75D8 | #75D3 | Station, банк 5, LD HL,#0000 | [HandleGameSettingsAction.asm](../Source/Station/HandleGameSettingsAction.asm) |

| Station | #7A2B | #E146 | D3D, банк 4, LD A,#00 | [SelectSaleMode.asm](../Source/Station/SelectSaleMode.asm) |

| Station | #7A35 | #68EB | Station, банк 5, LD A,#00 | [SelectSaleMode.asm](../Source/Station/SelectSaleMode.asm) |

| Station | #7A6B | #E146 | D3D, банк 4, LD A,#00 | [SelectPurchaseMode.asm](../Source/Station/SelectPurchaseMode.asm) |

| Station | #7A75 | #68EB | Station, банк 5, LD A,#00 | [SelectPurchaseMode.asm](../Source/Station/SelectPurchaseMode.asm) |

| Station | #7B1C | #71EC | Station, банк 5, LD A,#00 | [SelectEquipmentPurchase.asm](../Source/Station/SelectEquipmentPurchase.asm) |

| Station | #7B37 | #71EC | Station, банк 5, LD A,#00 | [SelectEquipmentSale.asm](../Source/Station/SelectEquipmentSale.asm) |

| Station | #7AC6 | #78D7 | Station, банк 5, LD A,#00 | [OpenMapPanelGroup.asm](../Source/Station/OpenMapPanelGroup.asm) |

| Station | #7430 | #7471 | Station, банк 5, LD A,#00 | [HandleSaveSlotAction.asm](../Source/Station/HandleSaveSlotAction.asm) |

| Station | #74C2 | #74FF | Station, банк 5, LD A,#00 | [HandleLoadSlotAction.asm](../Source/Station/HandleLoadSlotAction.asm) |

| Station | #784B | #9A89 | Station, банк 2, CALL #9A58 | [HandleSystemMapAction.asm](../Source/Station/HandleSystemMapAction.asm) |

| Station | #79D4 | #E146 | D3D, банк 4, LD A,#00 | [ConfirmShipModelTrade.asm](../Source/Station/ConfirmShipModelTrade.asm) |

| Station | #71A7 | #7217 | Station, банк 5, LD A,#FF | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #71AD | #A265 | Station, банк 2, CALL #0000 | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #71B3 | #A235 | Station, банк 2, LD DE,#0000 | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #71BE | #71B9 | Station, банк 5, LD HL,#0000 | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #71D5 | #6ACC | Station, банк 5, LD A,#00 | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #71DB | #6AA4 | Station, банк 5, LD HL,#0000 | [HandleEquipmentListAction.asm](../Source/Station/HandleEquipmentListAction.asm) |

| Station | #AA69 | #9A89 | Station, банк 2, CALL #9A58 | [HandleMissionGroupAction.asm](../Source/Station/HandleMissionGroupAction.asm) |

| Music | #DB97 | #DF6E | Music, банк 3, LD HL,nn по DF6D | [ReadEnvelopeSlide.asm](../Source/Music/ReadEnvelopeSlide.asm) |

| Music | #DDF2 | #DF25 | LD A,#00 | [SetGateTimingB.asm](../Source/Music/SetGateTimingB.asm) |

| Music | #DDF7 | #DF2D | LD A,#00 | [SetGateTimingB.asm](../Source/Music/SetGateTimingB.asm) |

| Music | #DDFC | #DF1E | JR #DF31 | [SetGateTimingB.asm](../Source/Music/SetGateTimingB.asm) |

| Music | #E60E | #DE7A | LD A,#00 | [SetToneSlideA.asm](../Source/Music/SetToneSlideA.asm) |

| Music | #E617 | #DE82 | LD HL,#0000 | [SetToneSlideA.asm](../Source/Music/SetToneSlideA.asm) |

| Music | #E61C | #DE88 | LD A,#00 | [SetToneSlideA.asm](../Source/Music/SetToneSlideA.asm) |

| Music | #E625 | #DE7A | LD A,#00 | [SetTonePortamentoA.asm](../Source/Music/SetTonePortamentoA.asm) |

| Music | #E630 | #DE82 | LD HL,#0000 | [SetTonePortamentoA.asm](../Source/Music/SetTonePortamentoA.asm) |

| Music | #E635 | #DE88 | LD A,#00 | [SetTonePortamentoA.asm](../Source/Music/SetTonePortamentoA.asm) |

| Music | #E63C | #DE75 | LD A,#00 | [SetTonePortamentoA.asm](../Source/Music/SetTonePortamentoA.asm) |

| Music | #E649 | #DEA6 | LD A,#00 | [SetSamplePositionA.asm](../Source/Music/SetSamplePositionA.asm) |

| Music | #E64E | #DEA3 | JR #DEAE | [SetSamplePositionA.asm](../Source/Music/SetSamplePositionA.asm) |

| Music | #E654 | #DEB1 | LD A,#00 | [SetOrnamentPositionA.asm](../Source/Music/SetOrnamentPositionA.asm) |

| Music | #E659 | #DEAE | JR #DEB9 | [SetOrnamentPositionA.asm](../Source/Music/SetOrnamentPositionA.asm) |

| Music | #E65F | #DF08 | LD A,#00 | [SetToneSlideB.asm](../Source/Music/SetToneSlideB.asm) |

| Music | #E668 | #DF10 | LD HL,#0000 | [SetToneSlideB.asm](../Source/Music/SetToneSlideB.asm) |

| Music | #E66D | #DF16 | LD A,#00 | [SetToneSlideB.asm](../Source/Music/SetToneSlideB.asm) |

| Music | #E676 | #DF08 | LD A,#00 | [SetTonePortamentoB.asm](../Source/Music/SetTonePortamentoB.asm) |

| Music | #E681 | #DF10 | LD HL,#0000 | [SetTonePortamentoB.asm](../Source/Music/SetTonePortamentoB.asm) |

| Music | #E686 | #DF16 | LD A,#00 | [SetTonePortamentoB.asm](../Source/Music/SetTonePortamentoB.asm) |

| Music | #E68D | #DF03 | LD A,#00 | [SetTonePortamentoB.asm](../Source/Music/SetTonePortamentoB.asm) |

| Music | #E69A | #DF34 | LD A,#00 | [SetSamplePositionB.asm](../Source/Music/SetSamplePositionB.asm) |

| Music | #E69F | #DF31 | JR #DF3C | [SetSamplePositionB.asm](../Source/Music/SetSamplePositionB.asm) |

| Music | #E6A5 | #DF3F | LD A,#00 | [SetOrnamentPositionB.asm](../Source/Music/SetOrnamentPositionB.asm) |

| Music | #E6AA | #DF3C | JR #DF47 | [SetOrnamentPositionB.asm](../Source/Music/SetOrnamentPositionB.asm) |

| Music | #E6CB | #E29D | LD A,#00 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6CE | #E2CC | LD A,#00 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6D9 | #E2A6 | LD HL,#0000 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6DE | #E2D5 | LD A,#00 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6E1 | #E2AD | JR #E2CB | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6E8 | #E2B1 | LD A,#00 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |

| Music | #E6F0 | #E1F9 | LD A,#00 | [SetSamplePositionC.asm](../Source/Music/SetSamplePositionC.asm) |

| Music | #E6F6 | #E27A | LD A,#00 | [SetOrnamentPositionC.asm](../Source/Music/SetOrnamentPositionC.asm) |

| Music | #E6FC | #DF62 | LD A,#03 | [SetRowTempo.asm](../Source/Music/SetRowTempo.asm) |

| Music | #E642 | #DE4D | LD A,#00 | [SetTonePortamentoA.asm](../Source/Music/SetTonePortamentoA.asm) |

| Music | #E693 | #DEDB | LD A,#00 | [SetTonePortamentoB.asm](../Source/Music/SetTonePortamentoB.asm) |

| Music | #E6EB | #E2B9 | CP #00 | [SetTonePortamentoC.asm](../Source/Music/SetTonePortamentoC.asm) |
| Music | #E0C3 | #E0BB | CP #00 | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E0C8 | #E098 | LD BC,#0000 | [RenderChannelA.asm](../Source/Music/RenderChannelA.asm) |
| Music | #E1C3 | #E1BB | CP #00 | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E1C8 | #E198 | LD BC,#0000 | [RenderChannelB.asm](../Source/Music/RenderChannelB.asm) |
| Music | #E2C1 | #E2B9 | CP #00 | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |
| Music | #E2C6 | #E296 | LD BC,#0000 | [RenderChannelC.asm](../Source/Music/RenderChannelC.asm) |

| Controls | #DE1D | #688B | `LD A,#00` | [BuildParameterTables.asm](../Source/Controls/BuildParameterTables.asm) |

Запись DE1D из банка 1 меняет операнд 688B общего ядра ACTION в фиксированном банке 5. Исходные байты целевой команды находятся в ACTION по смещению 0AC7, операнд по 0AC8, после переноса ядра. Цель находится в [UpdateBodyMotion.asm](../Source/Action/UpdateBodyMotion.asm), числовой индекс и проверка цепочки описаны в [ControlsParameterTables](ControlsParameterTables.md).

[ApplyParameterSet](ActionApplyParameters.md) записывает 15 целевых байтов, десять из них являются доказанными непосредственными операндами. В реестре уточнены физические банки и файловые смещения этих десяти целей. Пять Unknown-целей не объявляются кодом. Порядок выбора банка и аппаратная блокировка описаны в [ActionParameterActivation](ActionParameterActivation.md).

[UpdateGlyphIndicators](ControlsGlyphIndicators.md) записывает входной SP в операнд E089 команды LD SP,nn по E088 банка 1. Во время очистки SP направляется в пиксели, затем сохранённый операнд действительно восстанавливает рамку. Проверка охватывает записи операнда, 64 байта очистки и временные возвраты CALL.

## Полные слова обмена AD1D

[SwapCodePatchWords](../Source/Action/SwapCodePatchWords.asm) содержит шесть двухбайтовых записей, AD24→CB54, AD27→CB8B, AD32→CB6F, AD35→CBD8, AD40→CBBC, AD43→CBEE. Каждая изменяет операнд LD A,n и следующий префикс CB. [Границы и проверка](ActionPatchSwap.md) описывают оба байта каждого слова, замена на обмен только операндов не выполняется.

## Сохранение компонентов и SP в ACEA

[TransformVectorTransposed](../Source/Action/TransformVectorTransposed.asm) записывает входные слова, ACEE→AF48, ACF1→AF56, ACF5→AF69, и настоящий SP, ACFC→AD08. Все записи двухбайтовые, относятся к существующим операндам. [Рамка и продолжение](ActionVectorWrapper.md) описаны отдельно.

## Параметр записи и звук в 60AE

[CreateMissileForTarget](../Source/Action/CreateMissileForTarget.asm) записывает слово потока канала A, 60BB→ECA9 в банке 0, и байт параметра, 60E8→612E. Последний является непосредственным байтом LD (IY+Unknown13),n. [Три пути и банковый контекст](ActionMissileCreation.md) описаны отдельно.

## Общий хвост запуска ракет

[CompleteMissileLaunch](../Source/Action/CompleteMissileLaunch.asm) записывает слово потока AY-канала A, 7060→ECA9 в банке 0. При потерянной цели CreateMissileForTarget повторяет ту же запись. [Порядок и отказы](ActionMissileRequests.md) описаны отдельно.

## ReverseScaledVector

[ReverseScaledVector](../Source/Action/ReverseScaledVector.asm) обновляет существующие операнды в фиксированном банке 5 и банке 0 ACTION.

- 6EE0→6EAD, один байт допуска StepNearZeroWord, инструкция по 6EAC.
- 6EED→E5B3, слово Component0, инструкция по E5B2.
- 6EFA→E5ED, слово Component2, инструкция по E5EC.
- 6F07→E5D2, слово Component1, инструкция по E5D1.

[Алгоритм, порядок записей и ограничения](ActionVectorReverse.md) описаны отдельно. SignedWord по A78F является обычным состоянием, не изменяемым кодом.

## Код запрета близкой записи

Операнд E507 принадлежит [DispatchCloseRecord](../Source/Action/DispatchCloseRecord.asm). Установлены писатели.

- [A89F](../Source/Action/UpdateFrame.asm)→E507, один байт.
- [E54D](../Source/Action/ReverseCloseRecordState.asm)→E507, один байт.

[Уменьшение кода и различия входов](ActionCloseRecord.md) описаны отдельно.

## Писатели сопровождения и назначения цели

[FollowProjectedTarget](ActionAimFollow.md) записывает CompanionMask по E3C2, снимает Request по E3CC и дважды выбирает CursorA по E3D2 и E3ED. Все четыре писателя зарегистрированы с исходными размерами операндов, новые области RAM не выделяются. AbsoluteX и AbsoluteY остаются изменяемыми операндами LD BC,nn и LD DE,nn, которые заполняет PrepareProjectedBounds.

## Сохранение стеков чтения очереди

[ReadRenderQueue](ActionRenderQueueControl.md) использует SavedEntrySP по E4A7, записанный прологом UnknownE020, и SavedNodeSP по E4D6, который обновляет LoadNode по E4B2. Оба поля являются исходными двухбайтовыми операндами LD SP,nn. LoadNode сохраняет слово указателя узла на CPU-стеке, затем восстанавливает именно адрес этого слова перед CALL UpdateAyEffects. Изменяемые операнды и банковый контекст не являются новой выделенной памятью.

## Уточнение банковых записей кадра

[Блок A981..AA89](ActionBank4Writes.md) пишет OBJECT3D в банке 4, код ACTION банка 0 по совпадающим адресам не изменяется. 41 ошибочных связей исключены из таблицы инструкций, все 80 фактических записей сохранены в [отдельном банковом реестре](../Tools/Disasm/Reports/ActionBank4DataWrites.json).

## Девять коэффициентов ACTION

[BuildRenderCoefficients](ActionRenderCoefficients.md) имеет 18 прямых писателей девяти раздельных байтов Coeff11..Coeff33. Писатель и цель находятся в банке 0, записи OBJECT3D банка 4 по совпадающим адресам выделены в отдельный реестр. Новая непрерывная область матрицы не создаётся.

## Выходные коэффициенты композиции ACTION

[ComposeRenderMatrix](ActionRenderMatrix.md) содержит 39 прямых писателей девяти исходных операндов LD A,n банка 0. Целевые инструкции остаются в неразобранном диапазоне, их границы подтверждены линейным продолжением от непосредственного CALL D5C9. Назначение всей следующей процедуры этим не считается доказанным.

| Цель | Писатели банка 0 |
|---|---|
| D5FC | CB87, CE3A, CE65, CE8C, CEB7 |
| D60D | CD6E, CE09, CE1C |
| D61E | CC77, CE4E, CE77, CEA2, CECF |
| D62F | CBD4, CE40, CE6B, CE94, CEBF |
| D640 | CDB8, CE0F, CE22 |
| D651 | CCC7, CE56, CE7D, CEA8, CED7 |
| D662 | CC21, CE46, CE71, CE9C, CEC7 |
| D673 | CE02, CE15, CE28 |
| D684 | CD17, CE5E, CE83, CEAE, CEDF |

## ProjectRenderVertex

[ProjectRenderVertex](../Source/Action/ProjectRenderVertex.asm) обновляет следующие существующие операнды в контексте своего договора.

- D7D0→D9C3, 2 байт, инструкция по D9C2.

[Алгоритм и ограничения](./ActionPerspective.md) описаны отдельно.

## ProjectRenderVertexGroup

[ProjectRenderVertexGroup](../Source/Action/ProjectRenderVertexGroup.asm) обновляет следующие существующие операнды в контексте своего договора.

- D694→D79D, 2 байт, инструкция по D79C.
- D6A6→D706, 2 байт, инструкция по D705.
- D6B4→D73A, 2 байт, инструкция по D739.
- D6BA→D747, 2 байт, инструкция по D746.
- D6BE→D756, 2 байт, инструкция по D755.
- D6C9→D77B, 2 байт, инструкция по D77A.
- D6CD→D788, 2 байт, инструкция по D787.
- D6D3→D761, 2 байт, инструкция по D760.
- D6D9→D76E, 2 байт, инструкция по D76D.
- D6F6→D77E, 1 байт, инструкция по D77D.
- D6FA→D78B, 1 байт, инструкция по D78A.
- D6FE→D764, 1 байт, инструкция по D763.
- D702→D771, 1 байт, инструкция по D770.
- D799→D699, 1 байт, инструкция по D698.

[Алгоритм и ограничения](./ActionVertexGroup.md) описаны отдельно.

## PrepareRenderVertexProducts

[PrepareRenderVertexProducts](../Source/Action/PrepareRenderVertexProducts.asm) обновляет следующие существующие операнды в контексте своего договора.

- D609→D69D, 1 байт, инструкция по D69B.
- D61A→D6A0, 1 байт, инструкция по D69E.
- D62B→D6A3, 1 байт, инструкция по D6A1.
- D63C→D69C, 1 байт, инструкция по D69B.
- D64D→D69F, 1 байт, инструкция по D69E.
- D65E→D6A2, 1 байт, инструкция по D6A1.
- D66F→D6E2, 1 байт, инструкция по D6E0.
- D680→D6E1, 1 байт, инструкция по D6E0.
- D691→D6DF, 1 байт, инструкция по D6DE.

[Алгоритм и ограничения](./ActionVertexProducts.md) описаны отдельно.

## TransformObjectVertices

[TransformObjectVertices](../Source/Action/TransformObjectVertices.asm) обновляет следующие существующие операнды в контексте своего договора.

- D5D5→D699, 1 байт, инструкция по D698.

[Алгоритм и ограничения](./ActionObjectVertices.md) описаны отдельно.

## CheckFaceOrientation

[CheckFaceOrientation](../Source/Action/CheckFaceOrientation.asm) обновляет следующие существующие операнды в контексте своего договора.

- DFCF→DFE4, 2 байт, инструкция по DFE3.

[Алгоритм и ограничения](./ActionFaceOrientation.md) описаны отдельно.

## DrawLinearLine

[DrawLinearLine](../Source/Action/DrawLinearLine.asm) обновляет следующие существующие операнды в контексте своего договора.

- DDFC→DEED, 2 байт, инструкция по DEEC.

[Алгоритм и ограничения](./ActionLineRaster.md) описаны отдельно.

## Opcode четырёх ядер DrawLinearLine

[Растеризатор](ActionLineRaster.md) пишет первые байты инструкций, не только операнды. Контекст всех записей ACTION банка 0.

| Писатель | Цель | Исполняемые значения |
| --- | --- | --- |
| DE35 | DE3F | A1 AND C, B1 OR C, A9 XOR C |
| DE3B | DE42 | 30 JR NC, 38 JR C |
| DE68 | DE72 | A1 AND C, B1 OR C, A9 XOR C |
| DE6E | DE7C | 30 JR NC, 38 JR C |
| DE99 | DEA3 | A1 AND C, B1 OR C, A9 XOR C |
| DE9F | DEA6 | 30 JR NC, 38 JR C |
| DECC | DED6 | A1 AND C, B1 OR C, A9 XOR C |
| DED2 | DEE0 | 30 JR NC, 38 JR C |

Исходные NOP и исходные JR C сохраняются в собираемом образе. SavedSP по DEED записывает DDFC. Показатель MaskOffset по DE0F подготавливает вызывающий код, это отдельная запись вне растеризатора.

## Подготовители режима линии ACTION

Писатели DC52 и DDA0 банка 0 сохраняют 10 либо 18 в операнде DE0F инструкции ADD A,nn по DE0E. DC4E и DD9C обновляют рабочие байты PixelOpcode/BranchOpcode по 8D4E/8D4F. Поле заголовка 5..4 выбирает AND, OR либо XOR, значения 10 и 11 оба дают XOR. [Договоры подготовителей](ActionLineRaster.md) проверены на всех 256 заголовках и счётчиках 2..15. Родительские процедуры пока остаются в неразобранном бинарном диапазоне, этот статус в реестре писателей сохранён.

## PreparePolygonFill

[PreparePolygonFill](../Source/Action/PreparePolygonFill.asm) обновляет следующие существующие операнды в контексте своего договора.

- D517→D3B7, 1 байт, инструкция по D3B6.
- D537→D4C2, 1 байт, инструкция по D4C1.
- D53B→D4C4, 1 байт, инструкция по D4C3.
- D53E→D387, 1 байт, инструкция по D386.
- D54C→D275, 2 байт, инструкция по D274.
- D55C→D3B0, 2 байт, инструкция по D3AF.
- D56A→D1FF, 1 байт, инструкция по D1FE.
- D56D→D258, 1 байт, инструкция по D257.
- D5AA→D264, 2 байт, инструкция по D263.
- D5BA→D22A, 1 байт, инструкция по D229.
- D5BF→D22C, 1 байт, инструкция по D22B.

[Алгоритм и ограничения](./ActionPolygonPreparation.md) описаны отдельно.

## SelectPolygonRowLimit

[SelectPolygonRowLimit](../Source/Action/SelectPolygonRowLimit.asm) обновляет следующие существующие операнды в контексте своего договора.

- D4D0→D22A, 1 байт, инструкция по D229.
- D4D5→D22C, 1 байт, инструкция по D22B.
- D4DF→D22A, 1 байт, инструкция по D229.
- D4E4→D22C, 1 байт, инструкция по D22B.
- D4EA→D22A, 1 байт, инструкция по D229.
- D4EF→D22C, 1 байт, инструкция по D22B.

[Алгоритм и ограничения](./ActionPolygonRowSelection.md) описаны отдельно.

## UpdatePolygonLeftEdge

[UpdatePolygonLeftEdge](../Source/Action/UpdatePolygonLeftEdge.asm) обновляет следующие существующие операнды в контексте своего договора.

- D284→D275, 2 байт, инструкция по D274.
- D288→D217, 1 байт, инструкция по D216.
- D290→D4C4, 1 байт, инструкция по D4C3.
- D2DF→D213, 1 байт, инструкция по D212.
- D2FC→D213, 1 байт, инструкция по D212.
- D31C→D213, 1 байт, инструкция по D212.
- D36B→D213, 1 байт, инструкция по D212.
- D399→D213, 1 байт, инструкция по D212.
- D38D→D22A, 1 байт, инструкция по D229.
- D392→D22C, 1 байт, инструкция по D22B.

[Алгоритм и ограничения](./ActionPolygonLeftEdge.md) описаны отдельно.

## SetShortNegativeRightStep

[SetShortNegativeRightStep](../Source/Action/SetShortNegativeRightStep.asm) обновляет следующие существующие операнды в контексте своего договора.

- D4F5→D21F, 1 байт, инструкция по D21E.

[Алгоритм и ограничения](./ActionPolygonRightShortStep.md) описаны отдельно.

## UpdatePolygonRightEdge

[UpdatePolygonRightEdge](../Source/Action/UpdatePolygonRightEdge.asm) обновляет следующие существующие операнды в контексте своего договора.

- D3C2→D3B0, 2 байт, инструкция по D3AF.
- D3C6→D223, 1 байт, инструкция по D222.
- D3CF→D387, 1 байт, инструкция по D386.
- D41E→D21F, 1 байт, инструкция по D21E.
- D43A→D21F, 1 байт, инструкция по D21E.
- D459→D21F, 1 байт, инструкция по D21E.
- D4A6→D21F, 1 байт, инструкция по D21E.

[Алгоритм и ограничения](./ActionPolygonRightEdge.md) описаны отдельно.

## PolygonFillRows

[PolygonFillRows](../Source/Action/PolygonFillRows.asm) обновляет следующие существующие операнды в контексте своего договора.

- D239→D244, 1 байт, инструкция по D243.

[Алгоритм и ограничения](./ActionPolygonFillRows.md) описаны отдельно.

## RenderInsideRecords

[RenderInsideRecords](../Source/Action/RenderInsideRecords.asm) обновляет следующие существующие операнды в контексте своего договора.

- DD3E→D560, 1 байт, инструкция по D55F.

[Алгоритм и ограничения](./ActionPacketRenderer.md) описаны отдельно.

## RenderClippedRecords

[RenderClippedRecords](../Source/Action/RenderClippedRecords.asm) обновляет следующие существующие операнды в контексте своего договора.

- DBE2→D560, 1 байт, инструкция по D55F.

[Алгоритм и ограничения](./ActionClippedPacketRenderer.md) описаны отдельно.

## RequestTurnNegative

[RequestTurnNegative](../Source/Action/RequestTurnNegative.asm) обновляет следующие существующие операнды в контексте своего договора.

- 76C9→6FE5, 1 байт, инструкция по 6FE4.
- 76D0→76CD, 1 байт, инструкция по 76CC.
- 76D5→76F0, 1 байт, инструкция по 76EF.

[Алгоритм и ограничения](./ActionKeyTurnNegative.md) описаны отдельно.

## RequestTurnPositive

[RequestTurnPositive](../Source/Action/RequestTurnPositive.asm) обновляет следующие существующие операнды в контексте своего договора.

- 76EC→6FE5, 1 байт, инструкция по 6FE4.
- 76F3→76F0, 1 байт, инструкция по 76EF.
- 76F8→76CD, 1 байт, инструкция по 76CC.

[Алгоритм и ограничения](./ActionKeyTurnPositive.md) описаны отдельно.

## RequestXNegative

[RequestXNegative](../Source/Action/RequestXNegative.asm) обновляет следующие существующие операнды в контексте своего договора.

- 770F→6F7B, 1 байт, инструкция по 6F7A.
- 7716→7713, 1 байт, инструкция по 7712.
- 771B→7736, 1 байт, инструкция по 7735.

[Алгоритм и ограничения](./ActionKeyXNegative.md) описаны отдельно.

## RequestXPositive

[RequestXPositive](../Source/Action/RequestXPositive.asm) обновляет следующие существующие операнды в контексте своего договора.

- 7732→6F7B, 1 байт, инструкция по 6F7A.
- 7739→7736, 1 байт, инструкция по 7735.
- 773E→7713, 1 байт, инструкция по 7712.

[Алгоритм и ограничения](./ActionKeyXPositive.md) описаны отдельно.

## RequestYNegative

[RequestYNegative](../Source/Action/RequestYNegative.asm) обновляет следующие существующие операнды в контексте своего договора.

- 7755→6FB0, 1 байт, инструкция по 6FAF.
- 775C→7759, 1 байт, инструкция по 7758.
- 7761→777C, 1 байт, инструкция по 777B.

[Алгоритм и ограничения](./ActionKeyYNegative.md) описаны отдельно.

## RequestYPositive

[RequestYPositive](../Source/Action/RequestYPositive.asm) обновляет следующие существующие операнды в контексте своего договора.

- 7778→6FB0, 1 байт, инструкция по 6FAF.
- 777F→777C, 1 байт, инструкция по 777B.
- 7784→7759, 1 байт, инструкция по 7758.

[Алгоритм и ограничения](./ActionKeyYPositive.md) описаны отдельно.

## IncreaseGaugeWord

[IncreaseGaugeWord](../Source/Action/IncreaseGaugeWord.asm) обновляет следующие существующие операнды в контексте своего договора.

- 769F→669F, 1 байт, инструкция по 669E.

[Алгоритм и ограничения](./ActionKeyGaugeIncrease.md) описаны отдельно.

## DecreaseGaugeWord

[DecreaseGaugeWord](../Source/Action/DecreaseGaugeWord.asm) обновляет следующие существующие операнды в контексте своего договора.

- 76C3→669F, 1 байт, инструкция по 669E.

[Алгоритм и ограничения](./ActionKeyGaugeDecrease.md) описаны отдельно.

## AdvanceObjectPhaseWait

[AdvanceObjectPhaseWait](../Source/Action/AdvanceObjectPhaseWait.asm) обновляет следующие существующие операнды в контексте своего договора.

- EFBF→EFBD, 1 байт, инструкция по EFBC.

[Алгоритм и ограничения](./ActionObjectPhaseWait.md) описаны отдельно.

## PrepareObjectOffsetTransform

[PrepareObjectOffsetTransform](../Source/Action/PrepareObjectOffsetTransform.asm) обновляет следующие существующие операнды в контексте своего договора.

- F101→B045, 1 байт, инструкция по B044.
- F109→B04F, 1 байт, инструкция по B04E.
- F10F→B05C, 1 байт, инструкция по B05B.

[Алгоритм и ограничения](./ActionObjectOffsetTransfer.md) описаны отдельно.

## BuildObjectOffsetCoefficients

[BuildObjectOffsetCoefficients](../Source/Action/BuildObjectOffsetCoefficients.asm) обновляет следующие существующие операнды в контексте своего договора.

- B075→6D0E, 1 байт, инструкция по 6D0D.
- B0AD→6D1C, 1 байт, инструкция по 6D1B.
- B0E5→6D2A, 1 байт, инструкция по 6D29.

[Алгоритм и ограничения](./ActionObjectOffsetCoefficients.md) описаны отдельно.
