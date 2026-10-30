; -----------------------------------------
; запись 22, CONTROL0.C
; логическая длина 6878, полный секторный размер 6912
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified000.bin"
                assert $ == #0870
                disp #C870
                include "../Controls/UnknownC870.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0882
                disp #C882
                include "../Controls/UnknownC882.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A8D
                disp #CA8D
                include "../Controls/UnknownCA8D.asm"
                ent
                assert $ == #0AB3
                disp #CAB3
                include "../Controls/UnknownCAB3.asm"
                ent
                assert $ == #0AE3
                disp #CAE3
                include "../Controls/UnknownCAE3.asm"
                ent
                assert $ == #0B00
                disp #CB00
                include "../Controls/UnknownCB00.asm"
                ent
                assert $ == #0E16
                disp #CE16
                include "../Controls/UnknownCE16.asm"
                ent
                assert $ == #0E5D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified001.bin"
                assert $ == #0EA4
                disp #CEA4
                include "../Controls/UnknownCEA4.asm"
                ent
                assert $ == #0EB5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified002.bin"
                assert $ == #0ECF
                disp #CECF
                include "../Controls/UnknownCECF.asm"
                ent
                assert $ == #0EF9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified003.bin"
                assert $ == #0EFA
                disp #CEFA
                include "../Controls/UnknownCEFA.asm"
                ent
                assert $ == #0F0B
                disp #CF0B
                include "../Controls/UnknownCF0B.asm"
                ent
                assert $ == #10CA
                disp #D0CA
                include "../Controls/UnknownD0CA.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #110A
                disp #D10A
                include "../Controls/UnknownD10A.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1165
                disp #D165
                include "../Controls/UnknownD165.asm"                           ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1167
                disp #D167
                include "../Controls/UnknownD167.asm"                           ; (3) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #117D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified004.bin"
                assert $ == #118D
                disp #D18D
                include "../Controls/UnknownD18D.asm"
                ent
                assert $ == #11A2
                disp #D1A2
                include "../Controls/UnknownD1A2.asm"
                ent
                assert $ == #11B6
                disp #D1B6
                include "../Controls/UnknownD1B6.asm"
                ent
                assert $ == #11CB
                disp #D1CB
                include "../Controls/UnknownD1CB.asm"
                ent
                assert $ == #11DF
                disp #D1DF
                include "../Controls/UnknownD1DF.asm"
                ent
                assert $ == #11F4
                disp #D1F4
                include "../Controls/UnknownD1F4.asm"
                ent
                assert $ == #1208
                disp #D208
                include "../Controls/UnknownD208.asm"
                ent
                assert $ == #1211
                disp #D211
                include "../Controls/UnknownD211.asm"
                ent
                assert $ == #121A
                disp #D21A
                include "../Controls/UnknownD21A.asm"
                ent
                assert $ == #1227
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified005.bin"
                assert $ == #1232
                disp #D232
                include "../Controls/UnknownD232.asm"
                ent
                assert $ == #1236
                disp #D236
                include "../Controls/UnknownD236.asm"
                ent
                assert $ == #130B
                disp #D30B
                include "../Controls/UnknownD30B.asm"
                ent
                assert $ == #1320
                disp #D320
                include "../Controls/UnknownD320.asm"
                ent
                assert $ == #14CB
                disp #D4CB
                include "../Controls/UnknownD4CB.asm"
                ent
                assert $ == #14E4
                disp #D4E4
                include "../Controls/UnknownD4E4.asm"
                ent
                assert $ == #1501
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified006.bin"
                assert $ == #1504
                disp #D504
                include "../Controls/UnknownD504.asm"
                ent
                assert $ == #1515
                disp #D515
                include "../Controls/UnknownD515.asm"
                ent
                assert $ == #153C
                disp #D53C
                include "../Controls/UnknownD53C.asm"
                ent
                assert $ == #156C
                disp #D56C
                include "../Controls/UnknownD56C.asm"
                ent
                assert $ == #157B
                disp #D57B
                include "../Controls/UnknownD57B.asm"
                ent
                assert $ == #1609
                disp #D609
                include "../Controls/UnknownD609.asm"
                ent
                assert $ == #1717
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified007.bin"
                assert $ == #1727
                disp #D727
                include "../Controls/UnknownD727.asm"
                ent
                assert $ == #180F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified008.bin"
                assert $ == #1833
                disp #D833
                include "../Controls/UnknownD833.asm"
                ent
                assert $ == #1901
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified009.bin"
                assert $ == #1925
                disp #D925
                include "../Controls/UnknownD925.asm"
                ent
                assert $ == #1940
                disp #D940
                include "../Controls/UnknownD940.asm"
                ent
                assert $ == #195B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified010.bin"
                assert $ == #195F
                disp #D95F
                include "../Controls/UnknownD95F.asm"
                ent
                assert $ == #197E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified011.bin"
                assert $ == #19B0
                disp #D9B0
                include "../Controls/UnknownD9B0.asm"
                ent
                assert $ == #19DE
                disp #D9DE
                include "../Controls/UnknownD9DE.asm"
                ent
                assert $ == #1AB9
                disp #DAB9
                include "../Controls/UnknownDAB9.asm"
                ent
                assert $ == #1ADE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified012.bin"
                assert $ == #1B00
