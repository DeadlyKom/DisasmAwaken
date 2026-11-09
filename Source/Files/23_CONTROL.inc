; -----------------------------------------
; запись 23, CONTROL.C
; логическая длина 6474, полный секторный размер 6656
; -----------------------------------------
                assert $ == #0000
                disp #DADE
                include "../Controls/RunTemporaryModule.asm"
                ent
                assert $ == #007F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #007F
                disp #5E1F
                include "../Controls/LoadLegacyPackedBlock.asm"
                ent
                assert $ == #00AD
                disp #5E4D
                include "../Controls/ReadLegacySectors.asm"
                ent
                assert $ == #0132
                disp #5ED2
                include "../Controls/WriteLegacyDiskPort.asm"                   ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0136
                disp #5ED6
                include "../Controls/CallLegacyDosRom.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #013B
                ; Unknown, соседний диапазон сохраняется без классификации
                incbin "../Resources/23_CONTROL/Unclassified013B_01BD.bin"
                assert $ == #01BD
                disp #DC9B
                include "../Controls/RelocateStationReload.asm"
                ent
                assert $ == #01CB
                ; Unknown, соседние исходные байты перед подготовкой станции
                assert $ == #01CB
                disp #4000
                include "../Controls/LoadStationDirectRelay.asm"
                ent
                assert $ == #01FC
                ; Unknown, соседний диапазон сохраняется без классификации
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ControlsDirectStationRelay.md)
                assert $ == #01FC
                disp #4031
                include "../Controls/Data/DirectStationKey.asm"
                ent
                assert $ == #0205
                disp #DCE3
                include "../Controls/PrepareStationReload.asm"
                ent
                assert $ == #0245
                ; Unknown, переносимый загрузочный блок после подготовки станции
                assert $ == #0245
                disp #4200
                include "../Controls/LoadStationStateRelay.asm"
                ent
                assert $ == #0276
                ; Unknown, соседний диапазон сохраняется без классификации
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ControlsDirectStationRelay.md)
                assert $ == #0276
                disp #4231
                include "../Controls/Data/StateStationKey.asm"
                ent
                assert $ == #027F
                disp #DD5D
                include "../Controls/StepWordRandom.asm"
                ent
                assert $ == #02A9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                assert $ == #02A9
                disp #DD87
                include "../Controls/ResetFlightContext.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #032C
                disp #DE0A
                include "../Controls/BuildAndActivateParameters.asm"            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0332
                disp #DE10
                include "../Controls/BuildParameterTables.asm"
                ent
                assert $ == #03BC
                disp #DE9A
                include "../Controls/BuildSeededIndices.asm"
                ent
                assert $ == #03FE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ControlsParameterTables.md)
                assert $ == #03FE
                disp #DEDC
                include "../Controls/Data/ParameterRowGroups.asm"
                ent
                assert $ == #043E
                disp #DF1C
                include "../Controls/Data/ParameterLastRowGroup.asm"
                ent
                assert $ == #0447
                disp #DF25
                include "../Controls/Data/ParameterValueGroups.asm"
                ent
                assert $ == #0477
                disp #DF55
                include "../Controls/Data/ParameterLastValueGroup.asm"
                ent
                assert $ == #0486
                disp #DF64
                include "../Controls/Data/ParameterCoefficients.asm"
                ent
                assert $ == #04B3
                ; Unknown, исходные байты после правил параметров
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ControlsResetFlightContext.md)
                assert $ == #04B3
                disp #DF91
                include "../Controls/Data/VectorsNoDiablo.asm"
                ent
                assert $ == #04FB
                disp #DFD9
                include "../Controls/Data/VectorsWithDiablo.asm"
                ent
                assert $ == #0543
                disp #E021
                include "../Controls/UpdateGlyphIndicators.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0670
                disp #E14E
                include "../Controls/OrThreeRowGlyph.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06D3
                ; Четыре трёхстрочных знака, восемь исходных фаз каждого
                disp #E1B1
                include "../Controls/Data/ThreeRowGlyphs.asm"
                ent
                assert $ == #0793
                ; Физические адреса для перенаправленного RET, полный рисователь ещё Unknown
                disp #E271
                include "../Controls/Data/RasterReturns.asm"
                ent
                assert $ == #07B3
                disp #E291
                include "../Controls/DrawRadar.asm"
                ent
                assert $ == #0B7F
                ; Физические записи ControlsObjectGlyphPointers
                disp #E65D
                include "../Controls/Data/ObjectGlyphPointers.asm"
                ent
                assert $ == #0BA7
                ; Физические записи ControlsObjectPixelMasks
                disp #E685
                include "../Controls/Data/ObjectPixelMasks.asm"
                ent
                assert $ == #0BAF
                ; Физические записи ControlsObjectClearMasks
                disp #E68D
                include "../Controls/Data/ObjectClearMasks.asm"
                ent
                assert $ == #0BDF
                ; Физические записи ControlsObjectGlyphs
                disp #E6BD
                include "../Controls/Data/ObjectGlyphs.asm"
                ent
                assert $ == #0E1F
                disp #E8FD
                include "../Controls/DrawSixRowGauge.asm"
                ent
                assert $ == #0E95
                ; Семь физических масок частичного столбца шкалы
                disp #E973
                include "../Controls/Data/GaugeMasks.asm"
                ent
                assert $ == #0E9C
                disp #E97A
                include "../Controls/ToggleTargetOverlay.asm"
                ent
                assert $ == #1030
                disp #EB0E
                include "../Controls/Data/OverlayGlyphs.asm"
                ent
                assert $ == #1130
                disp #EC0E
                include "../Controls/InitializeTextWindow.asm"
                ent
                assert $ == #1178
                disp #EC56
                include "../Controls/QueueNumber.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #117B
                disp #EC59
                include "../Controls/QueueTextItem.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #11A2
                disp #EC80
                include "../Controls/Data/TextQueue.asm"
                ent
                assert $ == #11C4
                disp #ECA2
                include "../Controls/ConsumeTextQueue.asm"
                ent
                assert $ == #1215
                disp #ECF3
                include "../Controls/PrintByteDecimal.asm"
                ent
                assert $ == #124A
                disp #ED28
                include "../Controls/ScrollTextWindow.asm"
                ent
                assert $ == #14E6
                disp #EFC4
                include "../Controls/PrintTextGlyph.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1513
                disp #EFF1
                include "../Controls/DrawGlyphRows.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #15B6
                disp #F094
                include "../Controls/XorBufferMarker.asm"
                ent
                assert $ == #160F
                disp #F0ED
                include "../Controls/Data/MarkerPhaseMasks.asm"
                ent
                assert $ == #162F
                disp #F10D
                include "../Controls/TickBcdCounter.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1664
                disp #F142
                include "../Controls/DrawBcdCounter.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #16AA
                disp #F188
                include "../Controls/DrawCounterNibble.asm"                     ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #16CD
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                ; Документация [29 сообщений и секторный хвост](../../Docs/ControlsFlightMessages.md)
                incbin "../Controls/Resources/FlightMessages.bin"
                assert $ == #194A
                ; Unknown, 182 байта хвоста секторов после логического конца CONTROL
                ; Физический суффикс выделенных секторов, неиспользуемость не установлена
                ; Документация [границы и сохранение суффиксов](../../Docs/AllocatedSectorSuffixes.md)
                incbin "../Resources/23_CONTROL/SectorTail.bin"
                assert $ == #1A00
