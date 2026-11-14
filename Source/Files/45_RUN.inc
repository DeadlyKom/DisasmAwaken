                ; Архивный RUN.C, исходный вход #6000 и два экранных снимка.
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                assert $ == #0000
                disp #6000
                include "../ArchiveRun/RunMenu.asm"
                ent
                assert $ == #009A
                disp #609A
                include "../ArchiveRun/Data/LastKey.asm"
                ent
                assert $ == #009B
                disp #609B
                include "../ArchiveRun/MoveSelectionUp.asm"
                ent
                assert $ == #00BC
                disp #60BC
                include "../ArchiveRun/MoveSelectionDown.asm"
                ent
                assert $ == #00DF
                disp #60DF
                include "../ArchiveRun/InvokeSelection.asm"
                ent
                assert $ == #010A
                disp #610A
                include "../ArchiveRun/LoadStartFile.asm"
                ent
                assert $ == #0132
                disp #6132
                include "../ArchiveRun/Data/StartFileKey.asm"
                ent
                assert $ == #013B
                disp #613B
                include "../ArchiveRun/CopyScreen.asm"
                ent
                assert $ == #0144
                disp #6144
                include "../ArchiveRun/ClearSelectedScreen.asm"
                ent
                assert $ == #0159
                disp #6159
                include "../ArchiveRun/EnableMenuInterrupts.asm"
                ent
                assert $ == #0179
                disp #6179
                include "../ArchiveRun/MenuInterrupt.asm"
                ent
                assert $ == #01A6
                disp #61A6
                include "../ArchiveRun/Data/BlinkPeriod.asm"
                ent
                assert $ == #01A7
                disp #61A7
                include "../ArchiveRun/FindSelectionMarker.asm"
                ent
                assert $ == #01BD
                disp #61BD
                include "../ArchiveRun/ClearSelectionMarker.asm"                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #01CF
                disp #61CF
                include "../ArchiveRun/ClearMarkerColumn.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #01E1
                disp #61E1
                include "../ArchiveRun/ToggleSelectionMarker.asm"               ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #01F3
                disp #61F3
                include "../ArchiveRun/XorMarkerColumn.asm"                     ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0200
                disp #6200
                include "../ArchiveRun/SetVisibleScreen.asm"
                ent
                assert $ == #0213
                disp #6213
                include "../ArchiveRun/SelectDrawingScreen.asm"
                ent
                assert $ == #0228
                disp #6228
                include "../ArchiveRun/Data/VisibleScreen.asm"
                ent
                assert $ == #0229
                disp #6229
                include "../ArchiveRun/RenderMenu.asm"
                ent
                assert $ == #0277
                disp #6277
                include "../ArchiveRun/FinishMenuText.asm"
                ent
                assert $ == #027C
                disp #627C
                include "../ArchiveRun/XorMenuText.asm"
                ent
                assert $ == #02C6
                disp #62C6
                include "../ArchiveRun/Data/MenuState.asm"
                ent
                assert $ == #02CC
                disp #62CC
                include "../ArchiveRun/ShowOptions.asm"
                ent
                assert $ == #02D9
                disp #62D9
                include "../ArchiveRun/ShowMainMenu.asm"
                ent
                assert $ == #02E6
                disp #62E6
                include "../ArchiveRun/CycleMemoryMode.asm"
                ent
                assert $ == #0301
                disp #6301
                include "../ArchiveRun/XorModeCaption.asm"
                ent
                assert $ == #031C
                disp #631C
                include "../ArchiveRun/FindModeCaption.asm"
                ent
                assert $ == #0330
                disp #6330
                include "../ArchiveRun/Data/Menus.asm"
                ent
                assert $ == #038F
                disp #638F
                include "../ArchiveRun/PixelAddress.asm"
                ent
                assert $ == #03AA
                disp #63AA
                include "../ArchiveRun/NextBitmapRowHL.asm"
                ent
                assert $ == #03B9
                disp #63B9
                include "../ArchiveRun/NextBitmapRowDE.asm"
                ent
                assert $ == #03C8
                disp #63C8
                include "../ArchiveRun/PrevBitmapRowHL.asm"
                ent
                assert $ == #03DD
                disp #63DD
                include "../ArchiveRun/Data/Images.asm"
                ent
                assert $ == #3CDD
                ; Секторный хвост, включая следы прежнего каталога.
                incbin "../../Tools/Disasm/Extracted/Archived/45_RUN.C.tail.bin"
                assert $ == #3D00
