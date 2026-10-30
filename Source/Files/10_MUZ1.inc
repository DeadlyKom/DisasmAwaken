; -----------------------------------------
; запись 10, MUZ1.C
; логическая длина 7209, полный секторный размер 7424
; -----------------------------------------
                assert $ == #0000
                disp #DB00
                include "../Music/Initialize.asm"
                ent
                assert $ == #0005
                disp #DB05
                include "../Music/PlayFrame.asm"
                ent
                assert $ == #0008
                disp #DB08
                include "../Music/Stop.asm"
                ent
                assert $ == #000A
                disp #DB0A
                include "../Music/InitializeModule.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007C
                disp #DB7C
                include "../Music/ClearAyRegisters.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00A0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified000.bin"
                assert $ == #02CA
                disp #DDCA
                include "../Music/ReadGateTimingA.asm"
                ent
                assert $ == #02CE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified001.bin"
                assert $ == #02D2
                disp #DDD2
                include "../Music/SetGateTimingA.asm"
                ent
                assert $ == #02E0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified002.bin"
                assert $ == #030A
                disp #DE0A
                include "../Music/ReadGateTimingC.asm"
                ent
                assert $ == #030E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified003.bin"
                assert $ == #0312
                disp #DE12
                include "../Music/SetGateTimingC.asm"
                ent
                assert $ == #031E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified004.bin"
                assert $ == #031F
                disp #DE1F
                include "../Music/TickDispatch.asm"
                ent
                assert $ == #0374
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified005.bin"
                assert $ == #0390
                disp #DE90
                include "../Music/UnknownDE90.asm"
                ent
                assert $ == #03A5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified006.bin"
                assert $ == #03AE
                disp #DEAE
                include "../Music/UnknownDEAE.asm"
                ent
                assert $ == #03B0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified007.bin"
                assert $ == #03B9
                disp #DEB9
                include "../Music/UnknownDEB9.asm"
                ent
                assert $ == #0402
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified008.bin"
                assert $ == #041E
                disp #DF1E
                include "../Music/UnknownDF1E.asm"
                ent
                assert $ == #0420
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified009.bin"
                assert $ == #0431
                disp #DF31
                include "../Music/UnknownDF31.asm"
                ent
                assert $ == #0433
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified010.bin"
                assert $ == #043C
                disp #DF3C
                include "../Music/UnknownDF3C.asm"
                ent
                assert $ == #043E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified011.bin"
                assert $ == #0447
                disp #DF47
                include "../Music/UnknownDF47.asm"
                ent
                assert $ == #046D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified012.bin"
                assert $ == #0470
                disp #DF70
                include "../Music/UnknownDF70.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #047F
                disp #DF7F
                include "../Music/AdvancePatternA.asm"                          ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04E3
                disp #DFE3
                include "../Music/RenderChannelA.asm"                           ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05B0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified013.bin"
                assert $ == #05CD
                disp #E0CD
                include "../Music/UnknownE0CD.asm"
                ent
                assert $ == #06B0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified014.bin"
                assert $ == #06CD
                disp #E1CD
                include "../Music/UnknownE1CD.asm"
                ent
                assert $ == #07AE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified015.bin"
                assert $ == #07CB
                disp #E2CB
                include "../Music/UnknownE2CB.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0939
                disp #E439
                include "../Music/UnknownE439.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #09E6
                disp #E4E6
                include "../Music/UnknownE4E6.asm"                              ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A83
                disp #E583
                include "../Music/UnknownE583.asm"                              ; (3) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0B0C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified016.bin"
                assert $ == #0BAE
                disp #E6AE
                include "../Music/SetToneSlideC.asm"
                ent
                assert $ == #0BC9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified017.bin"
                assert $ == #0C00
                ; исходный ресурс PT3
                incbin "../Music/Resources/Antichrist.pt3"
                assert $ == #1C29
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/10_MUZ1/Unclassified018.bin"
                assert $ == #1D00
