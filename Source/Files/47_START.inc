                ; Архивный START.C, фиксированный вход #6000 и продолжение в окне #C000.
                ; Документация [загрузка и кадры](../../Docs/BankStripArchiveConsumer.md)
                assert $ == #0000
                disp #6000
                include "../ArchiveStart/RunBankMenu.asm"
                ent
                assert $ == #0062
                disp #6062
                include "../ArchiveStart/StageLeftStrip.asm"
                ent
                assert $ == #009C
                disp #609C
                include "../ArchiveStart/StageRightStrip.asm"
                ent
                assert $ == #00D6
                disp #60D6
                include "../ArchiveStart/Data/BankKeys.asm"
                ent
                assert $ == #010C
                disp #610C
                include "../ArchiveStart/Data/Routes.asm"
                ent
                assert $ == #0172
                disp #6172
                include "../ArchiveStart/LoadEngine.asm"
                ent
                assert $ == #018F
                disp #618F
                include "../ArchiveStart/Data/EngineKey.asm"
                ent
                assert $ == #0198
                disp #6198
                include "../ArchiveStart/HandleBankFrame.asm"
                ent
                assert $ == #021D
                disp #621D
                include "../ArchiveStart/ScanLeftKeys.asm"
                ent
                assert $ == #025A
                disp #625A
                include "../ArchiveStart/ScanRightKeys.asm"
                ent
                assert $ == #0297
                disp #6297
                include "../ArchiveStart/Data/SelectorKeys.asm"
                ent
                assert $ == #02F7
                disp #62F7
                include "../ArchiveStart/Data/SelectorSide.asm"
                ent
                assert $ == #02F8
                disp #62F8
                include "../ArchiveStart/ApplySelectorKey.asm"
                ent
                assert $ == #033F
                disp #633F
                include "../ArchiveStart/ShowScreen.asm"
                ent
                assert $ == #0349
                disp #6349
                include "../ArchiveStart/SelectScreenForDraw.asm"
                ent
                assert $ == #0350
                disp #6350
                include "../ArchiveStart/SelectBankIndex.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0358
                disp #6358
                include "../ArchiveStart/SelectPage.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #035B
                disp #635B
                include "../ArchiveStart/SelectScorpionPage.asm"
                ent
                assert $ == #037E
                disp #637E
                include "../ArchiveStart/SelectAtmPage.asm"
                ent
                assert $ == #03A7
                disp #63A7
                include "../ArchiveStart/OutputThroughDos.asm"
                ent
                assert $ == #03AE
                disp #63AE
                include "../ArchiveStart/SelectPentagonPage.asm"
                ent
                assert $ == #03D2
                disp #63D2
                include "../ArchiveStart/NextStripRow.asm"
                ent
                assert $ == #03E1
                incbin "../../Tools/Disasm/Extracted/Archived/47_START.C.sectors.bin", #03E1, #001F
                assert $ == #0400
                disp #6400
                include "../ArchiveStart/Data/MirrorTable.asm"
                ent
                assert $ == #0500
                disp #6500
                include "../ArchiveStart/LoadChooseScreen.asm"
                ent
                assert $ == #0520
                disp #6520
                include "../ArchiveStart/LoadBanks.asm"
                ent
                assert $ == #053A
                disp #653A
                include "../ArchiveStart/Data/LoadState.asm"
                ent
                assert $ == #053C
                disp #653C
                include "../ArchiveStart/LoadBankFile.asm"
                ent
                assert $ == #0552
                disp #6552
                include "../ArchiveStart/FillLayerAttributes.asm"
                ent
                assert $ == #0573
                disp #6573
                include "../ArchiveStart/DrawFirstLayer.asm"
                ent
                assert $ == #057A
                disp #657A
                include "../ArchiveStart/RestoreLayerStack.asm"
                ent
                assert $ == #057E
                disp #657E
                include "../ArchiveStart/DrawSecondLayer.asm"
                ent
                assert $ == #0585
                disp #6585
                include "../ArchiveStart/DrawThirdLayer.asm"
                ent
                assert $ == #058C
                disp #658C
                include "../ArchiveStart/MultiplyByteWord.asm"
                ent
                assert $ == #059D
                disp #659D
                include "../ArchiveStart/DrawLeftStaged.asm"
                ent
                assert $ == #05B0
                disp #65B0
                include "../ArchiveStart/DrawLeftDirect.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05C3
                disp #65C3
                include "../ArchiveStart/CopyLeftStrip.asm"                     ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05DB
                disp #65DB
                include "../ArchiveStart/ResolveStrip.asm"
                ent
                assert $ == #05E9
                disp #65E9
                include "../ArchiveStart/DrawRightStaged.asm"
                ent
                assert $ == #05FC
                disp #65FC
                include "../ArchiveStart/DrawRightDirect.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #060F
                disp #660F
                include "../ArchiveStart/CopyRightStrip.asm"                    ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0640
                disp #6640
                include "../ArchiveStart/Data/MenuData.asm"
                ent
                assert $ == #0665
                disp #6665
                include "../ArchiveStart/Data/TileMasks.asm"
                ent
                assert $ == #0725
                ; Две совпадающие 27-байтовые записи, назначение остаётся открытым.
                incbin "../../Tools/Disasm/Extracted/Archived/47_START.C.sectors.bin", #0725, #0036
                assert $ == #075B
                disp #675B
                include "../ArchiveStart/SetupInterrupts.asm"
                ent
                assert $ == #077C
                ; Нижние 14 нулевых байтов не использовались в двух проверенных профилях.
                incbin "../../Tools/Disasm/Extracted/Archived/47_START.C.sectors.bin", #077C, #000E
                assert $ == #078A
                disp #678A
                include "../ArchiveStart/Data/FrameStack.asm"
                ent
                assert $ == #07A4
                disp #67A4
                include "../ArchiveStart/FrameInterrupt.asm"
                ent
                assert $ == #07D7
                disp #67D7
                include "../ArchiveStart/Data/StripBuffers.asm"
                ent
                assert $ == #0C87
                ; Три исходных байта между буферами полос и исполняемыми слоями.
                incbin "../../Tools/Disasm/Extracted/Archived/47_START.C.sectors.bin", #0C87, #0003
                assert $ == #0C8A
                disp #6C8A
                include "../ArchiveStart/ThirdLayerProgram.asm"
                ent
                assert $ == #285C
                disp #885C
                include "../ArchiveStart/SecondLayerProgram.asm"
                ent
                assert $ == #442E
                disp #A42E
                include "../ArchiveStart/FirstLayerProgram.asm"
                ent
                assert $ == #6000
                disp #C000
                include "../ArchiveStart/Data/LayerWork.asm"
                ent
                assert $ == #6004
                disp #C004
                include "../ArchiveStart/PrepareRightLayerUpdate.asm"
                ent
                assert $ == #6026
                disp #C026
                include "../ArchiveStart/PrepareLeftLayerUpdate.asm"            ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6043
                disp #C043
                include "../ArchiveStart/RedrawLayerSelection.asm"              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6126
                disp #C126
                include "../ArchiveStart/WriteLastLayerTiles.asm"
                ent
                assert $ == #613F
                disp #C13F
                include "../ArchiveStart/WriteLayerVariant.asm"
                ent
                assert $ == #6163
                disp #C163
                include "../ArchiveStart/CalculateLayerOrigin.asm"
                ent
                assert $ == #6176
                disp #C176
                include "../ArchiveStart/CommitRightRoute.asm"
                ent
                assert $ == #61A4
                disp #C1A4
                include "../ArchiveStart/CommitLeftRoute.asm"
                ent
                assert $ == #61D2
                disp #C1D2
                include "../ArchiveStart/CopyRouteDescriptor.asm"
                ent
                assert $ == #61E7
                disp #C1E7
                include "../ArchiveStart/Data/RoutePointers.asm"
                ent
                assert $ == #61FF
                disp #C1FF
                include "../ArchiveStart/RebuildLayerMasks.asm"
                ent
                assert $ == #6280
                disp #C280
                include "../ArchiveStart/ApplyEndMasks.asm"
                ent
                assert $ == #6295
                disp #C295
                include "../ArchiveStart/ApplyLayerMasks.asm"
                ent
                assert $ == #62B3
                disp #C2B3
                include "../ArchiveStart/ApplyMaskTile.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #62B7
                disp #C2B7
                include "../ArchiveStart/ApplyOffsetTile.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #62D5
                disp #C2D5
                include "../ArchiveStart/Data/MaskPointers.asm"
                ent
                assert $ == #6305
                disp #C305
                include "../ArchiveStart/Data/TileOffsets.asm"
                ent
                assert $ == #6335
                disp #C335
                include "../ArchiveStart/BlendLayerTile.asm"
                ent
                assert $ == #6369
                disp #C369
                include "../ArchiveStart/Data/ModeTargets.asm"
                ent
                assert $ == #636F
                disp #C36F
                include "../ArchiveStart/Data/Layers.asm"
                ent
                assert $ == #7E6F
                disp #DE6F
                include "../ArchiveStart/Data/RouteTable.asm"
                ent
                assert $ == #80C7
                ; Секторный хвост начинается после двенадцатого маршрута.
                incbin "../../Tools/Disasm/Extracted/Archived/47_START.C.tail.bin"
                assert $ == #8100
