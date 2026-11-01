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
                assert $ == #008C
                disp #DB8C
                include "../Music/ReadEnvelopeSlide.asm"
                ent
                assert $ == #00A0
                disp #DBA0
                include "../Music/Data/DataPointers.asm"
                ent
                assert $ == #0100
                disp #DC00
                include "../Music/Data/AyBuffer.asm"
                ent
                assert $ == #010E
                disp #DC0E
                include "../Music/Data/RowCountersBC.asm"
                ent
                assert $ == #0110
                disp #DC10
                include "../Music/Data/Volumes.asm"
                ent
                assert $ == #0200
                disp #DD00
                include "../Music/Data/Periods.asm"
                ent
                assert $ == #02C0
                assert $ == #02C0
                disp #DDC0
                include "../Music/Data/EffectsA.asm"
                ent
                assert $ == #02CA
                disp #DDCA
                include "../Music/ReadGateTimingA.asm"
                ent
                assert $ == #02CE
                disp #DDCE
                include "../Music/Data/ExtraEffectsA.asm"
                ent
                assert $ == #02D2
                disp #DDD2
                include "../Music/SetGateTimingA.asm"
                ent
                assert $ == #02E0
                disp #DDE0
                include "../Music/Data/EffectsB.asm"
                ent
                assert $ == #02EA
                disp #DDEA
                include "../Music/ReadGateTimingB.asm"
                ent
                assert $ == #02EE
                disp #DDEE
                include "../Music/Data/ExtraEffectsB.asm"
                ent
                assert $ == #02F2
                disp #DDF2
                include "../Music/SetGateTimingB.asm"
                ent
                assert $ == #0300
                disp #DE00
                include "../Music/Data/EffectsC.asm"
                ent
                assert $ == #030A
                disp #DE0A
                include "../Music/ReadGateTimingC.asm"
                ent
                assert $ == #030E
                disp #DE0E
                include "../Music/Data/ExtraEffectsC.asm"
                ent
                assert $ == #0312
                disp #DE12
                include "../Music/SetGateTimingC.asm"
                ent
                assert $ == #031E
                disp #DE1E
                include "../Music/Data/RowCounterA.asm"
                ent
                assert $ == #031F
                assert $ == #031F
                disp #DE1F
                include "../Music/TickDispatch.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #0390
                disp #DE90
                include "../Music/StageGateAndSampleA.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #03AE
                disp #DEAE
                include "../Music/StageOrnamentA.asm"                           ; (2) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #03B9
                disp #DEB9
                include "../Music/StageChannelBRow.asm"                         ; (3) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #041E
                disp #DF1E
                include "../Music/StageGateB.asm"                               ; (4) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #0431
                disp #DF31
                include "../Music/StageSampleB.asm"                             ; (5) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #043C
                disp #DF3C
                include "../Music/StageOrnamentB.asm"                           ; (6) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #0447
                disp #DF47
                include "../Music/StageEnvelopeAndNoise.asm"                    ; (7) жёсткий порядок, последовательное исполнение
                ent

                assert $ == #0470
                disp #DF70
                include "../Music/CommitEnvelopeSlide.asm"                      ; (8) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #047F
                disp #DF7F
                include "../Music/AdvancePatternA.asm"                          ; (9) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04E3
                disp #DFE3
                include "../Music/RenderChannelA.asm"                           ; (10) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05CD
                disp #E0CD
                include "../Music/FinishChannelA.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05ED
                disp #E0ED
                include "../Music/RenderChannelB.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06CD
                disp #E1CD
                include "../Music/FinishChannelB.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06ED
                disp #E1ED
                include "../Music/RenderChannelC.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07CB
                disp #E2CB
                include "../Music/FinishChannelC.asm"                           ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #07EB
                disp #E2EB
                include "../Music/OutputAyFrame.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #087C
                disp #E37C
                include "../Music/AdvancePatternBC.asm"                         ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #08DC
                disp #E3DC
                include "../Music/PatternCommandsA.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0939
                disp #E439
                include "../Music/DecodePatternA.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0989
                disp #E489
                include "../Music/PatternCommandsB.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #09E6
                disp #E4E6
                include "../Music/DecodePatternB.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A3D
                disp #E53D
                include "../Music/PatternCommandsC.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A83
                disp #E583
                include "../Music/DecodePatternC.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0B0C
                disp #E60C
                include "../Music/SetToneSlideA.asm"
                ent
                assert $ == #0B23
                disp #E623
                include "../Music/SetTonePortamentoA.asm"
                ent
                assert $ == #0B47
                disp #E647
                include "../Music/SetSamplePositionA.asm"
                ent
                assert $ == #0B52
                disp #E652
                include "../Music/SetOrnamentPositionA.asm"
                ent
                assert $ == #0B5D
                disp #E65D
                include "../Music/SetToneSlideB.asm"
                ent
                assert $ == #0B74
                disp #E674
                include "../Music/SetTonePortamentoB.asm"
                ent
                assert $ == #0B98
                disp #E698
                include "../Music/SetSamplePositionB.asm"
                ent
                assert $ == #0BA3
                disp #E6A3
                include "../Music/SetOrnamentPositionB.asm"
                ent
                assert $ == #0BAE
                disp #E6AE
                include "../Music/SetToneSlideC.asm"
                ent
                assert $ == #0BC9
                disp #E6C9
                include "../Music/SetTonePortamentoC.asm"
                ent
                assert $ == #0BEE
                disp #E6EE
                include "../Music/SetSamplePositionC.asm"
                ent
                assert $ == #0BF4
                disp #E6F4
                include "../Music/SetOrnamentPositionC.asm"
                ent
                assert $ == #0BFA
                disp #E6FA
                include "../Music/SetRowTempo.asm"
                ent
                assert $ == #0C00
                ; Исходная композиция, физический порядок записей сохранён
                disp #E700
                include "../Music/Composition/Header.asm"
                ent
                assert $ == #0C69
                disp #E769
                include "../Music/Composition/SampleOffsets.asm"
                ent
                assert $ == #0CA9
                disp #E7A9
                include "../Music/Composition/OrnamentOffsets.asm"
                ent
                assert $ == #0CC9
                disp #E7C9
                include "../Music/Composition/Positions.asm"
                ent
                assert $ == #0CE6
                disp #E7E6
                include "../Music/Composition/PatternOffsets.asm"
                ent
                assert $ == #0D58
                disp #E858
                include "../Music/Composition/Patterns/PatternA00.asm"
                ent
                assert $ == #0D89
                disp #E889
                include "../Music/Composition/Patterns/PatternA01.asm"
                ent
                assert $ == #0DBA
                disp #E8BA
                include "../Music/Composition/Patterns/PatternA02.asm"
                ent
                assert $ == #0E07
                disp #E907
                include "../Music/Composition/Patterns/PatternA03.asm"
                ent
                assert $ == #0E4E
                disp #E94E
                include "../Music/Composition/Patterns/PatternA04.asm"
                ent
                assert $ == #0E95
                disp #E995
                include "../Music/Composition/Patterns/PatternA05.asm"
                ent
                assert $ == #0EB6
                disp #E9B6
                include "../Music/Composition/Patterns/PatternA06.asm"
                ent
                assert $ == #0EDB
                disp #E9DB
                include "../Music/Composition/Patterns/PatternA07.asm"
                ent
                assert $ == #0F04
                disp #EA04
                include "../Music/Composition/Patterns/PatternA08.asm"
                ent
                assert $ == #0F31
                disp #EA31
                include "../Music/Composition/Patterns/PatternA0A.asm"
                ent
                assert $ == #0F62
                disp #EA62
                include "../Music/Composition/Patterns/PatternA0B.asm"
                ent
                assert $ == #0F93
                disp #EA93
                include "../Music/Composition/Patterns/PatternA0C.asm"
                ent
                assert $ == #0FC5
                disp #EAC5
                include "../Music/Composition/Patterns/PatternA0D.asm"
                ent
                assert $ == #100A
                disp #EB0A
                include "../Music/Composition/Patterns/PatternA0E.asm"
                ent
                assert $ == #104F
                disp #EB4F
                include "../Music/Composition/Patterns/PatternA0F.asm"
                ent
                assert $ == #1099
                disp #EB99
                include "../Music/Composition/Patterns/PatternA10.asm"
                ent
                assert $ == #10BD
                disp #EBBD
                include "../Music/Composition/Patterns/PatternA11.asm"
                ent
                assert $ == #10E1
                disp #EBE1
                include "../Music/Composition/Patterns/PatternA12.asm"
                ent
                assert $ == #1109
                disp #EC09
                include "../Music/Composition/Patterns/PatternB00.asm"
                ent
                assert $ == #11CD
                disp #ECCD
                include "../Music/Composition/Patterns/PatternB01.asm"
                ent
                assert $ == #1291
                disp #ED91
                include "../Music/Composition/Patterns/PatternB02.asm"
                ent
                assert $ == #136B
                disp #EE6B
                include "../Music/Composition/Patterns/PatternB03.asm"
                ent
                assert $ == #1441
                disp #EF41
                include "../Music/Composition/Patterns/PatternB05.asm"
                ent
                assert $ == #1456
                disp #EF56
                include "../Music/Composition/Patterns/PatternB06.asm"
                ent
                assert $ == #146B
                disp #EF6B
                include "../Music/Composition/Patterns/PatternB07.asm"
                ent
                assert $ == #1484
                disp #EF84
                include "../Music/Composition/Patterns/PatternB08.asm"
                ent
                assert $ == #14A1
                disp #EFA1
                include "../Music/Composition/Patterns/PatternB0D.asm"
                ent
                assert $ == #14AA
                disp #EFAA
                include "../Music/Composition/Patterns/PatternB0E.asm"
                ent
                assert $ == #14B3
                disp #EFB3
                include "../Music/Composition/Patterns/PatternB10.asm"
                ent
                assert $ == #15B7
                disp #F0B7
                include "../Music/Composition/Patterns/PatternB11.asm"
                ent
                assert $ == #16BB
                disp #F1BB
                include "../Music/Composition/Patterns/PatternB12.asm"
                ent
                assert $ == #17BC
                disp #F2BC
                include "../Music/Composition/Patterns/PatternC00.asm"
                ent
                assert $ == #1826
                disp #F326
                include "../Music/Composition/Patterns/PatternC01.asm"
                ent
                assert $ == #1890
                disp #F390
                include "../Music/Composition/Patterns/PatternC04.asm"
                ent
                assert $ == #18F5
                disp #F3F5
                include "../Music/Composition/Patterns/PatternC05.asm"
                ent
                assert $ == #1912
                disp #F412
                include "../Music/Composition/Patterns/PatternC06.asm"
                ent
                assert $ == #192F
                disp #F42F
                include "../Music/Composition/Patterns/PatternC07.asm"
                ent
                assert $ == #193E
                disp #F43E
                include "../Music/Composition/Patterns/PatternC08.asm"
                ent
                assert $ == #1954
                disp #F454
                include "../Music/Composition/Patterns/PatternC0D.asm"
                ent
                assert $ == #19BE
                disp #F4BE
                include "../Music/Composition/Patterns/PatternC0E.asm"
                ent
                assert $ == #1A28
                disp #F528
                include "../Music/Composition/Patterns/PatternC0F.asm"
                ent
                assert $ == #1A88
                disp #F588
                include "../Music/Composition/Samples/Sample01.asm"
                ent
                assert $ == #1ABA
                disp #F5BA
                include "../Music/Composition/Samples/Sample02.asm"
                ent
                assert $ == #1AC0
                disp #F5C0
                include "../Music/Composition/Samples/Sample03.asm"
                ent
                assert $ == #1AC6
                disp #F5C6
                include "../Music/Composition/Samples/Sample04.asm"
                ent
                assert $ == #1AE4
                disp #F5E4
                include "../Music/Composition/Samples/Sample05.asm"
                ent
                assert $ == #1B16
                disp #F616
                include "../Music/Composition/Samples/Sample06.asm"
                ent
                assert $ == #1B20
                disp #F620
                include "../Music/Composition/Samples/Sample07.asm"
                ent
                assert $ == #1B32
                disp #F632
                include "../Music/Composition/Samples/Sample08.asm"
                ent
                assert $ == #1B64
                disp #F664
                include "../Music/Composition/Samples/Sample0B.asm"
                ent
                assert $ == #1B82
                disp #F682
                include "../Music/Composition/Samples/Sample0C.asm"
                ent
                assert $ == #1B94
                disp #F694
                include "../Music/Composition/Samples/Sample0E.asm"
                ent
                assert $ == #1BAE
                disp #F6AE
                include "../Music/Composition/Samples/Sample0F.asm"
                ent
                assert $ == #1BD4
                disp #F6D4
                include "../Music/Composition/Ornaments/Ornament00.asm"
                ent
                assert $ == #1BD7
                disp #F6D7
                include "../Music/Composition/Ornaments/Ornament01.asm"
                ent
                assert $ == #1BDC
                disp #F6DC
                include "../Music/Composition/Ornaments/Ornament02.asm"
                ent
                assert $ == #1BE1
                disp #F6E1
                include "../Music/Composition/Ornaments/Ornament03.asm"
                ent
                assert $ == #1BE6
                disp #F6E6
                include "../Music/Composition/Ornaments/Ornament04.asm"
                ent
                assert $ == #1BEC
                disp #F6EC
                include "../Music/Composition/Ornaments/Ornament05.asm"
                ent
                assert $ == #1BF2
                disp #F6F2
                include "../Music/Composition/Ornaments/Ornament06.asm"
                ent
                assert $ == #1BF8
                disp #F6F8
                include "../Music/Composition/Ornaments/Ornament07.asm"
                ent
                assert $ == #1BFE
                disp #F6FE
                include "../Music/Composition/Ornaments/Ornament08.asm"
                ent
                assert $ == #1C04
                disp #F704
                include "../Music/Composition/Ornaments/Ornament09.asm"
                ent
                assert $ == #1C0A
                disp #F70A
                include "../Music/Composition/Ornaments/Ornament0A.asm"
                ent
                assert $ == #1C12
                disp #F712
                include "../Music/Composition/Ornaments/Ornament0B.asm"
                ent
                assert $ == #1C1E
                disp #F71E
                include "../Music/Composition/Ornaments/Ornament0C.asm"
                ent
                assert $ == #1C22
                disp #F722
                include "../Music/Composition/Ornaments/Ornament0D.asm"
                ent
                assert $ == #1C29
                assert $ == #1C29
                ; Исходные 215 байтов секторного хвоста за логическим концом MUZ1.C, сохраняются целиком
                incbin "../Music/Resources/SectorTail.bin"
                assert $ == #1D00
