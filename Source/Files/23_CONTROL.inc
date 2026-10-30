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
                include "../Controls/UnknownDD5D.asm"
                ent
                assert $ == #02A9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified002.bin"
                assert $ == #032C
                disp #DE0A
                include "../Controls/UnknownDE0A.asm"
                ent
                assert $ == #0332
                disp #DE10
                include "../Controls/UnknownDE10.asm"
                ent
                assert $ == #03BC
                disp #DE9A
                include "../Controls/UnknownDE9A.asm"
                ent
                assert $ == #03FE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified003.bin"
                assert $ == #0543
                disp #E021
                include "../Controls/UnknownE021.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0670
                disp #E14E
                include "../Controls/UnknownE14E.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06D3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified004.bin"
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
                include "../Controls/UnknownEC0E.asm"
                ent
                assert $ == #1178
                disp #EC56
                include "../Controls/UnknownEC56.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #117B
                disp #EC59
                include "../Controls/UnknownEC59.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #11A2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified008.bin"
                assert $ == #11C4
                disp #ECA2
                include "../Controls/UnknownECA2.asm"
                ent
                assert $ == #1215
                disp #ECF3
                include "../Controls/UnknownECF3.asm"
                ent
                assert $ == #124A
                disp #ED28
                include "../Controls/UnknownED28.asm"
                ent
                assert $ == #14E6
                disp #EFC4
                include "../Controls/UnknownEFC4.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1513
                disp #EFF1
                include "../Controls/UnknownEFF1.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #15B6
                disp #F094
                include "../Controls/UnknownF094.asm"
                ent
                assert $ == #160F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified009.bin"
                assert $ == #162F
                disp #F10D
                include "../Controls/UnknownF10D.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1664
                disp #F142
                include "../Controls/UnknownF142.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #16AA
                disp #F188
                include "../Controls/UnknownF188.asm"                           ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #16CD
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/23_CONTROL/Unclassified010.bin"
                assert $ == #1A00
