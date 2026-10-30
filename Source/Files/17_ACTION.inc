; -----------------------------------------
; запись 17, ACTION.C
; логическая длина 40960, полный секторный размер 40960
; -----------------------------------------
                assert $ == #0000
                disp #6000
                include "../ActionBoot/RelocateBootstrap.asm"
                ent
                assert $ == #0043
                disp #4200
                include "../ActionBoot/InitializeFlight.asm"
                ent
                assert $ == #00EE
                disp #42AB
                include "../ActionBoot/GetFileLocation.asm"
                ent
                assert $ == #0109
                disp #42C6
                include "../ActionBoot/LoadFileToBank.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #010C
                disp #42C9
                include "../ActionBoot/LoadFileAtAddress.asm"                   ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0113
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified000.bin"
                assert $ == #0149
                disp #4306
                include "../ActionBoot/InitializeRandomStates.asm"
                ent
                assert $ == #0198
                disp #4355
                include "../ActionBoot/BuildProjectionTable.asm"
                ent
                assert $ == #01D2
                disp #438F
                include "../ActionBoot/BuildReciprocalTable.asm"
                ent
                assert $ == #0212
                disp #43CF
                include "../ActionBoot/BuildBitmapTables.asm"
                ent
                assert $ == #023D
                disp #6000
                include "../Action/Unknown6000.asm"
                ent
                assert $ == #024D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified001.bin"
                assert $ == #027D
                disp #6040
                include "../Action/Unknown6040.asm"
                ent
                assert $ == #02EB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified002.bin"
                assert $ == #0382
                disp #6145
                include "../Action/Unknown6145.asm"
                ent
                assert $ == #03AF
                disp #6172
                include "../Action/Unknown6172.asm"
                ent
                assert $ == #03BA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified003.bin"
                assert $ == #04A2
                disp #6265
                include "../Action/Unknown6265.asm"
                ent
                assert $ == #04F2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified004.bin"
                assert $ == #050C
                disp #62CF
                include "../Action/Unknown62CF.asm"
                ent
                assert $ == #054E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified005.bin"
                assert $ == #0598
                disp #635B
                include "../Action/Unknown635B.asm"
                ent
                assert $ == #05F3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified006.bin"
                assert $ == #071C
                disp #64DF
                include "../Action/Unknown64DF.asm"
                ent
                assert $ == #072D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified007.bin"
                assert $ == #0876
                disp #6639
                include "../Action/Unknown6639.asm"
                ent
                assert $ == #0886
                disp #6649
                include "../Action/Unknown6649.asm"
                ent
                assert $ == #090F
                disp #66D2
                include "../Action/Unknown66D2.asm"
                ent
                assert $ == #09BD
                disp #6780
                include "../Action/Unknown6780.asm"
                ent
                assert $ == #0BBA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified008.bin"
                assert $ == #0BC3
                disp #6986
                include "../Action/Unknown6986.asm"
                ent
                assert $ == #0BD9
                disp #699C
                include "../Action/Unknown699C.asm"
                ent
                assert $ == #0BFB
                disp #69BE
                include "../Action/Unknown69BE.asm"
                ent
                assert $ == #0C66
                disp #6A29
                include "../Action/Unknown6A29.asm"
                ent
                assert $ == #0CAB
                disp #6A6E
                include "../Action/Unknown6A6E.asm"
                ent
                assert $ == #0CEA
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified009.bin"
                assert $ == #0CED
                disp #6AB0
                include "../Action/Unknown6AB0.asm"
                ent
                assert $ == #0D53
                disp #6B16
                include "../Action/Unknown6B16.asm"
                ent
                assert $ == #0E3C
                disp #6BFF
                include "../Action/Unknown6BFF.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E56
                disp #6C19
                include "../Action/Unknown6C19.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0E7D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified010.bin"
                assert $ == #0E80
                disp #6C43
                include "../Action/Unknown6C43.asm"
                ent
                assert $ == #0EBB
                disp #6C7E
                include "../Action/Unknown6C7E.asm"
                ent
                assert $ == #0ECC
                disp #6C8F
                include "../Action/Unknown6C8F.asm"
                ent
                assert $ == #0EEE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified011.bin"
                assert $ == #0EF1
                disp #6CB4
                include "../Action/Unknown6CB4.asm"
                ent
                assert $ == #0F13
                disp #6CD6
                include "../Action/Unknown6CD6.asm"
                ent
                assert $ == #0F21
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified012.bin"
                assert $ == #0F2C
                disp #6CEF
                include "../Action/Unknown6CEF.asm"
                ent
                assert $ == #0F3D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified013.bin"
                assert $ == #0F75
                disp #6D38
                include "../Action/Unknown6D38.asm"
                ent
                assert $ == #100E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified014.bin"
                assert $ == #1068
                disp #6E2B
                include "../Action/Unknown6E2B.asm"
                ent
                assert $ == #10A9
                disp #6E6C
                include "../Action/Unknown6E6C.asm"
                ent
                assert $ == #10E9
                disp #6EAC
                include "../Action/Unknown6EAC.asm"
                ent
                assert $ == #111B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified015.bin"
                assert $ == #115A
                disp #6F1D
                include "../Action/Unknown6F1D.asm"
                ent
                assert $ == #118B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified016.bin"
                assert $ == #1192
                disp #6F55
                include "../Action/Unknown6F55.asm"
                ent
                assert $ == #1254
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified017.bin"
                assert $ == #1738
                disp #74FB
                include "../Action/Unknown74FB.asm"
                ent
                assert $ == #1741
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified018.bin"
                assert $ == #1A96
                disp #7859
                include "../Action/Unknown7859.asm"
                ent
                assert $ == #1D03
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified019.bin"
                assert $ == #1D95
                disp #7B58
                include "../Action/Unknown7B58.asm"
                ent
                assert $ == #20DA
                disp #7E9D
                include "../Action/Unknown7E9D.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #20F4
                disp #7EB7
                include "../Action/Unknown7EB7.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #214B
                disp #7F0E
                include "../Action/Unknown7F0E.asm"
                ent
                assert $ == #21B3
                disp #7F76
                include "../Action/Unknown7F76.asm"
                ent
                assert $ == #21CC
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified020.bin"
                assert $ == #482D
                disp #A82D
                include "../Action/StartFlight.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #4859
                disp #A859
                include "../Action/MainLoop.asm"                                ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #485E
                disp #A85E
                include "../Action/UpdateFrame.asm"
                ent
                assert $ == #4ACC
                disp #AACC
                include "../Action/UnknownAACC.asm"
                ent
                assert $ == #4AE2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified021.bin"
                assert $ == #4B1B
                disp #AB1B
                include "../Action/SelectMemoryPage.asm"
                ent
                assert $ == #4B23
                disp #AB23
                include "../Action/UnpackResource.asm"
                ent
                assert $ == #4C38
                disp #AC38
                include "../Action/UnknownAC38.asm"
                ent
                assert $ == #4C5D
                disp #AC5D
                include "../Action/UnknownAC5D.asm"
                ent
                assert $ == #4CAB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified022.bin"
                assert $ == #4D48
                disp #AD48
                include "../Action/UnknownAD48.asm"
                ent
                assert $ == #4D5A
                disp #AD5A
                include "../Action/UnknownAD5A.asm"
                ent
                assert $ == #4DB7
                disp #ADB7
                include "../Action/UnknownADB7.asm"
                ent
                assert $ == #4DC5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified023.bin"
                assert $ == #4E24
                disp #AE24
                include "../Action/UnknownAE24.asm"
                ent
                assert $ == #4E73
                disp #AE73
                include "../Action/UnknownAE73.asm"
                ent
                assert $ == #4FF5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified024.bin"
                assert $ == #50E9
                disp #B0E9
                include "../Action/UnknownB0E9.asm"
                ent
                assert $ == #516F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified025.bin"
                assert $ == #6000
                disp #C000
                include "../Action/DispatchEdges.asm"
                ent
                assert $ == #6071
                disp #C071
                include "../Action/NextEdge.asm"                                ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #607A
                disp #C07A
                include "../Action/EdgeCase11.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #607B
                disp #C07B
                include "../Action/EdgeCase05.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #608A
                disp #C08A
                include "../Action/EdgeCase15.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6095
                disp #C095
                include "../Action/EdgeCase06.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60A4
                disp #C0A4
                include "../Action/EdgeCase46.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60AF
                disp #C0AF
                include "../Action/EdgeCase09.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60BE
                disp #C0BE
                include "../Action/EdgeCase89.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60C9
                disp #C0C9
                include "../Action/EdgeCase0A.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60D8
                disp #C0D8
                include "../Action/EdgeCase2A.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #60E3
                disp #C0E3
                include "../Action/EdgeCase10.asm"
                ent
                assert $ == #60E9
                disp #C0E9
                include "../Action/EdgeCase12.asm"
                ent
                assert $ == #60EF
                disp #C0EF
                include "../Action/EdgeCase14.asm"
                ent
                assert $ == #6101
                disp #C101
                include "../Action/EdgeCase16.asm"
                ent
                assert $ == #6119
                disp #C119
                include "../Action/EdgeCase18.asm"
                ent
                assert $ == #612B
                disp #C12B
                include "../Action/EdgeCase19.asm"
                ent
                assert $ == #6132
                disp #C132
                include "../Action/EdgeCase1A.asm"
                ent
                assert $ == #6144
                disp #C144
                include "../Action/EdgeCase20.asm"
                ent
                assert $ == #614A
                disp #C14A
                include "../Action/EdgeCase21.asm"
                ent
                assert $ == #6150
                disp #C150
                include "../Action/EdgeCase24.asm"
                ent
                assert $ == #6162
                disp #C162
                include "../Action/EdgeCase25.asm"
                ent
                assert $ == #6174
                disp #C174
                include "../Action/EdgeCase26.asm"
                ent
                assert $ == #617B
                disp #C17B
                include "../Action/EdgeCase28.asm"
                ent
                assert $ == #618D
                disp #C18D
                include "../Action/EdgeCase29.asm"
                ent
                assert $ == #61A5
                disp #C1A5
                include "../Action/EdgeCase40.asm"
                ent
                assert $ == #61AB
                disp #C1AB
                include "../Action/EdgeCase41.asm"
                ent
                assert $ == #61BD
                disp #C1BD
                include "../Action/EdgeCase42.asm"
                ent
                assert $ == #61CF
                disp #C1CF
                include "../Action/EdgeCase45.asm"
                ent
                assert $ == #61D6
                disp #C1D6
                include "../Action/EdgeCase48.asm"
                ent
                assert $ == #61DC
                disp #C1DC
                include "../Action/EdgeCase49.asm"
                ent
                assert $ == #61F1
                disp #C1F1
                include "../Action/EdgeCase4A.asm"
                ent
                assert $ == #620C
                disp #C20C
                include "../Action/EdgeCase50.asm"
                ent
                assert $ == #6228
                disp #C228
                include "../Action/EdgeCase51.asm"
                ent
                assert $ == #622F
                disp #C22F
                include "../Action/EdgeCase52.asm"
                ent
                assert $ == #624E
                disp #C24E
                include "../Action/EdgeCase54.asm"
                ent
                assert $ == #6259
                disp #C259
                include "../Action/EdgeCase56.asm"
                ent
                assert $ == #625F
                disp #C25F
                include "../Action/EdgeCase58.asm"
                ent
                assert $ == #6274
                disp #C274
                include "../Action/EdgeCase5A.asm"
                ent
                assert $ == #628D
                disp #C28D
                include "../Action/EdgeCase60.asm"
                ent
                assert $ == #62A9
                disp #C2A9
                include "../Action/EdgeCase61.asm"
                ent
                assert $ == #62BE
                disp #C2BE
                include "../Action/EdgeCase62.asm"
                ent
                assert $ == #62C9
                disp #C2C9
                include "../Action/EdgeCase64.asm"
                ent
                assert $ == #62D0
                disp #C2D0
                include "../Action/EdgeCase68.asm"
                ent
                assert $ == #62EF
                disp #C2EF
                include "../Action/EdgeCase69.asm"
                ent
                assert $ == #6308
                disp #C308
                include "../Action/EdgeCase6A.asm"
                ent
                assert $ == #630E
                disp #C30E
                include "../Action/EdgeCase80.asm"
                ent
                assert $ == #6314
                disp #C314
                include "../Action/EdgeCase81.asm"
                ent
                assert $ == #6326
                disp #C326
                include "../Action/EdgeCase82.asm"
                ent
                assert $ == #6338
                disp #C338
                include "../Action/EdgeCase84.asm"
                ent
                assert $ == #633E
                disp #C33E
                include "../Action/EdgeCase85.asm"
                ent
                assert $ == #6359
                disp #C359
                include "../Action/EdgeCase86.asm"
                ent
                assert $ == #636E
                disp #C36E
                include "../Action/EdgeCase8A.asm"
                ent
                assert $ == #6375
                disp #C375
                include "../Action/EdgeCase90.asm"
                ent
                assert $ == #6391
                disp #C391
                include "../Action/EdgeCase91.asm"
                ent
                assert $ == #639C
                disp #C39C
                include "../Action/EdgeCase92.asm"
                ent
                assert $ == #63B1
                disp #C3B1
                include "../Action/EdgeCase94.asm"
                ent
                assert $ == #63D0
                disp #C3D0
                include "../Action/EdgeCase95.asm"
                ent
                assert $ == #63D6
                disp #C3D6
                include "../Action/EdgeCase96.asm"
                ent
                assert $ == #63EF
                disp #C3EF
                include "../Action/EdgeCase98.asm"
                ent
                assert $ == #63F6
                disp #C3F6
                include "../Action/EdgeCaseA0.asm"
                ent
                assert $ == #6412
                disp #C412
                include "../Action/EdgeCaseA1.asm"
                ent
                assert $ == #6431
                disp #C431
                include "../Action/EdgeCaseA2.asm"
                ent
                assert $ == #6438
                disp #C438
                include "../Action/EdgeCaseA4.asm"
                ent
                assert $ == #644D
                disp #C44D
                include "../Action/EdgeCaseA5.asm"
                ent
                assert $ == #6466
                disp #C466
                include "../Action/EdgeCaseA8.asm"
                ent
                assert $ == #6471
                disp #C471
                include "../Action/EdgeCaseA9.asm"
                ent
                assert $ == #6477
                disp #C477
                include "../Action/UnknownC477.asm"
                ent
                assert $ == #6496
                disp #C496
                include "../Action/UnknownC496.asm"
                ent
                assert $ == #64B5
                disp #C4B5
                include "../Action/UnknownC4B5.asm"
                ent
                assert $ == #64D4
                disp #C4D4
                include "../Action/UnknownC4D4.asm"
                ent
                assert $ == #64F3
                disp #C4F3
                include "../Action/EdgeCase08.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #64F6
                disp #C4F6
                include "../Action/UnknownC4F6.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #653D
                disp #C53D
                include "../Action/EdgeCase04.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6540
                disp #C540
                include "../Action/UnknownC540.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6588
                disp #C588
                include "../Action/EdgeCase02.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #658B
                disp #C58B
                include "../Action/UnknownC58B.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #65E4
                disp #C5E4
                include "../Action/EdgeCase01.asm"                              ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #65E7
                disp #C5E7
                include "../Action/UnknownC5E7.asm"                             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #6641
                disp #C641
                include "../Action/UnknownC641.asm"
                ent
                assert $ == #664C
                disp #C64C
                include "../Action/UnknownC64C.asm"
                ent
                assert $ == #6657
                disp #C657
                include "../Action/UnknownC657.asm"
                ent
                assert $ == #6662
                disp #C662
                include "../Action/UnknownC662.asm"
                ent
                assert $ == #666D
                disp #C66D
                include "../Action/UnknownC66D.asm"
                ent
                assert $ == #6681
                disp #C681
                include "../Action/UnknownC681.asm"
                ent
                assert $ == #6695
                disp #C695
                include "../Action/UnknownC695.asm"
                ent
                assert $ == #66A9
                disp #C6A9
                include "../Action/UnknownC6A9.asm"
                ent
                assert $ == #66BD
                disp #C6BD
                include "../Action/UnknownC6BD.asm"
                ent
                assert $ == #66C8
                disp #C6C8
                include "../Action/UnknownC6C8.asm"
                ent
                assert $ == #66D3
                disp #C6D3
                include "../Action/EdgeCase00.asm"
                ent
                assert $ == #66EA
                disp #C6EA
                include "../Action/EdgeCase59.asm"
                ent
                assert $ == #66F4
                disp #C6F4
                include "../Action/UnknownC6F4.asm"
                ent
                assert $ == #688C
                disp #C88C
                include "../Action/UnknownC88C.asm"
                ent
                assert $ == #6EE3
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified026.bin"
                assert $ == #6F08
                disp #CF08
                include "../Action/UnknownCF08.asm"
                ent
                assert $ == #6F0B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified027.bin"
                assert $ == #710A
                disp #D10A
                include "../Action/ClearWorkBuffer.asm"
                ent
                assert $ == #712C
                disp #D12C
                include "../Action/MultiplySignedScaled.asm"
                ent
                assert $ == #7194
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified028.bin"
                assert $ == #8020
                disp #E020
                include "../Action/UnknownE020.asm"
                ent
                assert $ == #81B9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified029.bin"
                assert $ == #84A6
                disp #E4A6
                include "../Action/UnknownE4A6.asm"
                ent
                assert $ == #84DB
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified030.bin"
                assert $ == #84FF
                disp #E4FF
                include "../Action/UnknownE4FF.asm"
                ent
                assert $ == #8506
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified031.bin"
                assert $ == #855C
                disp #E55C
                include "../Action/UnknownE55C.asm"
                ent
                assert $ == #859F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified032.bin"
                assert $ == #85A0
                disp #E5A0
                include "../Action/UnknownE5A0.asm"
                ent
                assert $ == #8655
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified033.bin"
                assert $ == #8658
                disp #E658
                include "../Action/UnknownE658.asm"
                ent
                assert $ == #865F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified034.bin"
                assert $ == #8685
                disp #E685
                include "../Action/UnknownE685.asm"
                ent
                assert $ == #869E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified035.bin"
                assert $ == #86BE
                disp #E6BE
                include "../Action/UnknownE6BE.asm"
                ent
                assert $ == #86C5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified036.bin"
                assert $ == #86C7
                disp #E6C7
                include "../Action/UnknownE6C7.asm"
                ent
                assert $ == #86D1
                disp #E6D1
                include "../Action/UnknownE6D1.asm"
                ent
                assert $ == #86E2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified037.bin"
                assert $ == #898D
                disp #E98D
                include "../Action/UnknownE98D.asm"
                ent
                assert $ == #89A1
                disp #E9A1
                include "../Action/UnknownE9A1.asm"
                ent
                assert $ == #89C2
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified038.bin"
                assert $ == #8A29
                disp #EA29
                include "../Action/UnknownEA29.asm"
                ent
                assert $ == #8A3D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified039.bin"
                assert $ == #8B72
                disp #EB72
                include "../Action/UnknownEB72.asm"
                ent
                assert $ == #8B79
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified040.bin"
                assert $ == #8B87
                disp #EB87
                include "../Action/UnknownEB87.asm"
                ent
                assert $ == #8B8E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified041.bin"
                assert $ == #8BB8
                disp #EBB8
                include "../Action/UnknownEBB8.asm"
                ent
                assert $ == #8BBF
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified042.bin"
                assert $ == #8C08
                disp #EC08
                include "../Action/UnknownEC08.asm"
                ent
                assert $ == #8C54
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified043.bin"
                assert $ == #8CA8
                disp #ECA8
                include "../Action/UnknownECA8.asm"
                ent
                assert $ == #8D8F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified044.bin"
                assert $ == #9075
                disp #F075
                include "../Action/UnknownF075.asm"
                ent
                assert $ == #907C
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified045.bin"
                assert $ == #9394
                disp #F394
                include "../Action/UnknownF394.asm"
                ent
                assert $ == #93A1
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified046.bin"
                assert $ == #951E
                disp #F51E
                include "../Action/UnknownF51E.asm"
                ent
                assert $ == #9527
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified047.bin"
                assert $ == #9535
                disp #F535
                include "../Action/UnknownF535.asm"
                ent
                assert $ == #953F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified048.bin"
                assert $ == #9541
                disp #F541
                include "../Action/UnknownF541.asm"
                ent
                assert $ == #954B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified049.bin"
                assert $ == #954D
                disp #F54D
                include "../Action/UnknownF54D.asm"
                ent
                assert $ == #9557
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified050.bin"
                assert $ == #9572
                disp #F572
                include "../Action/UnknownF572.asm"
                ent
                assert $ == #957F
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified051.bin"
                assert $ == #9729
                disp #F729
                include "../Action/UpdateObjects.asm"
                ent
                assert $ == #9775
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified052.bin"
                assert $ == #9792
                disp #F792
                include "../Action/UnknownF792.asm"
                ent
                assert $ == #97BF
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified053.bin"
                assert $ == #97C6
                disp #F7C6
                include "../Action/UnknownF7C6.asm"
                ent
                assert $ == #9866
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/17_ACTION/Unclassified054.bin"
                assert $ == #A000
