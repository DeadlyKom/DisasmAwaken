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
                incbin "../Resources/23_CONTROL/Unclassified000.bin"
                assert $ == #01BD
                disp #DC9B
                include "../Controls/UnknownDC9B.asm"
                ent
                assert $ == #01CB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified001.bin"
                assert $ == #027F
                disp #DD5D
                include "../Controls/StepWordRandom.asm"
                ent
                assert $ == #02A9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified002.bin"
                assert $ == #032C
                disp #DE0A
                include "../Controls/BuildAndActivateParameters.asm"
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
                incbin "../Resources/23_CONTROL/Unclassified003_BeforeCoefficients.bin"
                assert $ == #0486
                disp #DF64
                include "../Controls/Data/ParameterCoefficients.asm"
                ent
                assert $ == #04B3
                ; Unknown, исходные байты после правил параметров
                incbin "../Resources/23_CONTROL/Unclassified003_AfterCoefficients.bin"
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
                include "../Controls/UnknownE291.asm"
                ent
                assert $ == #0B7F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified005.bin"
                assert $ == #0E1F
                disp #E8FD
                include "../Controls/UnknownE8FD.asm"
                ent
                assert $ == #0E95
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified006.bin"
                assert $ == #0E9C
                disp #E97A
                include "../Controls/UnknownE97A.asm"
                ent
                assert $ == #1030
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified007.bin"
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
                incbin "../Resources/23_CONTROL/Unclassified010.bin"
                assert $ == #1A00
