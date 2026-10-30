; -----------------------------------------
; запись 19, 3DPART.C
; логическая длина 8224, полный секторный размер 8448
; -----------------------------------------
                assert $ == #0000
                disp #C000
                include "../ThreeD/DispatchEdges.asm"
                ent
                assert $ == #0071
                disp #C071
                include "../ThreeD/NextEdge.asm"                                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007A
                disp #C07A
                include "../ThreeD/EdgeCase11.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007B
                disp #C07B
                include "../ThreeD/EdgeCase05.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #008A
                disp #C08A
                include "../ThreeD/EdgeCase15.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0095
                disp #C095
                include "../ThreeD/EdgeCase06.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00A4
                disp #C0A4
                include "../ThreeD/EdgeCase46.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00AF
                disp #C0AF
                include "../ThreeD/EdgeCase09.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00BE
                disp #C0BE
                include "../ThreeD/EdgeCase89.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00C9
                disp #C0C9
                include "../ThreeD/EdgeCase0A.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00D8
                disp #C0D8
                include "../ThreeD/EdgeCase2A.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00E3
                disp #C0E3
                include "../ThreeD/EdgeCase10.asm"
                ent
                assert $ == #00E9
                disp #C0E9
                include "../ThreeD/EdgeCase12.asm"
                ent
                assert $ == #00EF
                disp #C0EF
                include "../ThreeD/EdgeCase14.asm"
                ent
                assert $ == #0101
                disp #C101
                include "../ThreeD/EdgeCase16.asm"
                ent
                assert $ == #0119
                disp #C119
                include "../ThreeD/EdgeCase18.asm"
                ent
                assert $ == #012B
                disp #C12B
                include "../ThreeD/EdgeCase19.asm"
                ent
                assert $ == #0132
                disp #C132
                include "../ThreeD/EdgeCase1A.asm"
                ent
                assert $ == #0144
                disp #C144
                include "../ThreeD/EdgeCase20.asm"
                ent
                assert $ == #014A
                disp #C14A
                include "../ThreeD/EdgeCase21.asm"
                ent
                assert $ == #0150
                disp #C150
                include "../ThreeD/EdgeCase24.asm"
                ent
                assert $ == #0162
                disp #C162
                include "../ThreeD/EdgeCase25.asm"
                ent
                assert $ == #0174
                disp #C174
                include "../ThreeD/EdgeCase26.asm"
                ent
                assert $ == #017B
                disp #C17B
                include "../ThreeD/EdgeCase28.asm"
                ent
                assert $ == #018D
                disp #C18D
                include "../ThreeD/EdgeCase29.asm"
                ent
                assert $ == #01A5
                disp #C1A5
                include "../ThreeD/EdgeCase40.asm"
                ent
                assert $ == #01AB
                disp #C1AB
                include "../ThreeD/EdgeCase41.asm"
                ent
                assert $ == #01BD
                disp #C1BD
                include "../ThreeD/EdgeCase42.asm"
                ent
                assert $ == #01CF
                disp #C1CF
                include "../ThreeD/EdgeCase45.asm"
                ent
                assert $ == #01D6
                disp #C1D6
                include "../ThreeD/EdgeCase48.asm"
                ent
                assert $ == #01DC
                disp #C1DC
                include "../ThreeD/EdgeCase49.asm"
                ent
                assert $ == #01F1
                disp #C1F1
                include "../ThreeD/EdgeCase4A.asm"
                ent
                assert $ == #020C
                disp #C20C
                include "../ThreeD/EdgeCase50.asm"
                ent
                assert $ == #0228
                disp #C228
                include "../ThreeD/EdgeCase51.asm"
                ent
                assert $ == #022F
                disp #C22F
                include "../ThreeD/EdgeCase52.asm"
                ent
                assert $ == #024E
                disp #C24E
                include "../ThreeD/EdgeCase54.asm"
                ent
                assert $ == #0259
                disp #C259
                include "../ThreeD/EdgeCase56.asm"
                ent
                assert $ == #025F
                disp #C25F
                include "../ThreeD/EdgeCase58.asm"
                ent
                assert $ == #0274
                disp #C274
                include "../ThreeD/EdgeCase5A.asm"
                ent
                assert $ == #028D
                disp #C28D
                include "../ThreeD/EdgeCase60.asm"
                ent
                assert $ == #02A9
                disp #C2A9
                include "../ThreeD/EdgeCase61.asm"
                ent
                assert $ == #02BE
                disp #C2BE
                include "../ThreeD/EdgeCase62.asm"
                ent
                assert $ == #02C9
                disp #C2C9
                include "../ThreeD/EdgeCase64.asm"
                ent
                assert $ == #02D0
                disp #C2D0
                include "../ThreeD/EdgeCase68.asm"
                ent
                assert $ == #02EF
                disp #C2EF
                include "../ThreeD/EdgeCase69.asm"
                ent
                assert $ == #0308
                disp #C308
                include "../ThreeD/EdgeCase6A.asm"
                ent
                assert $ == #030E
                disp #C30E
                include "../ThreeD/EdgeCase80.asm"
                ent
                assert $ == #0314
                disp #C314
                include "../ThreeD/EdgeCase81.asm"
                ent
                assert $ == #0326
                disp #C326
                include "../ThreeD/EdgeCase82.asm"
                ent
                assert $ == #0338
                disp #C338
                include "../ThreeD/EdgeCase84.asm"
                ent
                assert $ == #033E
                disp #C33E
                include "../ThreeD/EdgeCase85.asm"
                ent
                assert $ == #0359
                disp #C359
                include "../ThreeD/EdgeCase86.asm"
                ent
                assert $ == #036E
                disp #C36E
                include "../ThreeD/EdgeCase8A.asm"
                ent
                assert $ == #0375
                disp #C375
                include "../ThreeD/EdgeCase90.asm"
                ent
                assert $ == #0391
                disp #C391
                include "../ThreeD/EdgeCase91.asm"
                ent
                assert $ == #039C
                disp #C39C
                include "../ThreeD/EdgeCase92.asm"
                ent
                assert $ == #03B1
                disp #C3B1
                include "../ThreeD/EdgeCase94.asm"
                ent
                assert $ == #03D0
                disp #C3D0
                include "../ThreeD/EdgeCase95.asm"
                ent
                assert $ == #03D6
                disp #C3D6
                include "../ThreeD/EdgeCase96.asm"
                ent
                assert $ == #03EF
                disp #C3EF
                include "../ThreeD/EdgeCase98.asm"
                ent
                assert $ == #03F6
                disp #C3F6
                include "../ThreeD/EdgeCaseA0.asm"
                ent
                assert $ == #0412
                disp #C412
                include "../ThreeD/EdgeCaseA1.asm"
                ent
                assert $ == #0431
                disp #C431
                include "../ThreeD/EdgeCaseA2.asm"
                ent
                assert $ == #0438
                disp #C438
                include "../ThreeD/EdgeCaseA4.asm"
                ent
                assert $ == #044D
                disp #C44D
                include "../ThreeD/EdgeCaseA5.asm"
                ent
                assert $ == #0466
                disp #C466
                include "../ThreeD/EdgeCaseA8.asm"
                ent
                assert $ == #0471
                disp #C471
                include "../ThreeD/EdgeCaseA9.asm"
                ent
                assert $ == #0477
                disp #C477
                include "../ThreeD/UnknownC477.asm"
                ent
                assert $ == #0496
                disp #C496
                include "../ThreeD/UnknownC496.asm"
                ent
                assert $ == #04B5
                disp #C4B5
                include "../ThreeD/UnknownC4B5.asm"
                ent
                assert $ == #04D4
                disp #C4D4
                include "../ThreeD/UnknownC4D4.asm"
                ent
                assert $ == #04F3
                disp #C4F3
                include "../ThreeD/EdgeCase08.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04F6
                disp #C4F6
                include "../ThreeD/UnknownC4F6.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #053D
                disp #C53D
                include "../ThreeD/EdgeCase04.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0540
                disp #C540
                include "../ThreeD/UnknownC540.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0588
                disp #C588
                include "../ThreeD/EdgeCase02.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #058B
                disp #C58B
                include "../ThreeD/UnknownC58B.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05E4
                disp #C5E4
                include "../ThreeD/EdgeCase01.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05E7
                disp #C5E7
                include "../ThreeD/UnknownC5E7.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0641
                disp #C641
                include "../ThreeD/UnknownC641.asm"
                ent
                assert $ == #064C
                disp #C64C
                include "../ThreeD/UnknownC64C.asm"
                ent
                assert $ == #0657
                disp #C657
                include "../ThreeD/UnknownC657.asm"
                ent
                assert $ == #0662
                disp #C662
                include "../ThreeD/UnknownC662.asm"
                ent
                assert $ == #066D
                disp #C66D
                include "../ThreeD/UnknownC66D.asm"
                ent
                assert $ == #0681
                disp #C681
                include "../ThreeD/UnknownC681.asm"
                ent
                assert $ == #0695
                disp #C695
                include "../ThreeD/UnknownC695.asm"
                ent
                assert $ == #06A9
                disp #C6A9
                include "../ThreeD/UnknownC6A9.asm"
                ent
                assert $ == #06BD
                disp #C6BD
                include "../ThreeD/UnknownC6BD.asm"
                ent
                assert $ == #06C8
                disp #C6C8
                include "../ThreeD/UnknownC6C8.asm"
                ent
                assert $ == #06D3
                disp #C6D3
                include "../ThreeD/EdgeCase00.asm"
                ent
                assert $ == #06EA
                disp #C6EA
                include "../ThreeD/EdgeCase59.asm"
                ent
                assert $ == #06F4
                disp #C6F4
                include "../ThreeD/UnknownC6F4.asm"
                ent
                assert $ == #088C
                disp #C88C
                include "../ThreeD/UnknownC88C.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0AB3
                disp #CAB3
                include "../ThreeD/UnknownCAB3.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0AE3
                disp #CAE3
                include "../ThreeD/UnknownCAE3.asm"                             ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0EE3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/19_3DPART/Unclassified000.bin"
                assert $ == #0F08
                disp #CF08
                include "../ThreeD/UnknownCF08.asm"
                ent
                assert $ == #0F0B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/19_3DPART/Unclassified001.bin"
                assert $ == #110A
                disp #D10A
                include "../ThreeD/ClearWorkBuffer.asm"
                ent
                assert $ == #112C
                disp #D12C
                include "../ThreeD/MultiplySignedScaled.asm"
                ent
                assert $ == #1194
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/19_3DPART/Unclassified002.bin"
                assert $ == #2100
