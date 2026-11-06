; -----------------------------------------
; запись 22, CONTROL0.C
; логическая длина 6878, полный секторный размер 6912
; -----------------------------------------
                assert $ == #0000
                disp #C000
                include "../Controls/Data/RootCache.asm"
                ent
                assert $ == #0300
                disp #C300
                include "../Controls/Data/Squares.asm"
                ent
                assert $ == #0500
                disp #C500
                include "../Controls/Data/BufferPoints.asm"
                ent
                assert $ == #0546
                ; Unknown, исходные байты после физических записей координат
                incbin "../Resources/22_CONTROL0/Unclassified000_Suffix.bin"
                assert $ == #0870
                disp #C870
                include "../Controls/CopyViewportToScreen.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0882
                disp #C882
                include "../Controls/CopyScreenRows.asm"                        ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0A8D
                disp #CA8D
                include "../Controls/NextBufferRandom.asm"
                ent
                assert $ == #0AB3
                disp #CAB3
                include "../Controls/InitializeBufferPoints.asm"
                ent
                assert $ == #0AE3
                disp #CAE3
                include "../Controls/XorBufferPoints.asm"
                ent
                assert $ == #0B00
                disp #CB00
                include "../Controls/UpdateBufferPoints.asm"
                ent
                assert $ == #0E16
                disp #CE16
                include "../Controls/RespawnPointIndexPos.asm"
                ent
                assert $ == #0E5D
                disp #CE5D
                include "../Controls/RespawnPointIndexNeg.asm"
                ent
                assert $ == #0EA4
                disp #CEA4
                include "../Controls/FillEvenSpan.asm"
                ent
                assert $ == #0EB5
                ; Два байта CEB5..CEB6 не достигаются при A=0..15, назначение отдельно не установлено
                incbin "../Resources/22_CONTROL0/Unclassified002_Prefix.bin"
                assert $ == #0EB7
                disp #CEB7
                include "../Controls/FillEvenSpanHead.asm"                      ; (0) жёсткий порядок, начало непрерывного хвоста
                ent
                assert $ == #0ECF
                disp #CECF
                include "../Controls/FillEvenSpanTail.asm"                      ; (1) жёсткий порядок, продолжение хвоста
                ent
                assert $ == #0EF9
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified003.bin"
                assert $ == #0EFA
                disp #CEFA
                include "../Controls/ProjectAndDrawBody.asm"
                ent
                assert $ == #0F0B
                disp #CF0B
                include "../Controls/BuildBodyProjection.asm"
                ent
                assert $ == #10CA
                disp #D0CA
                include "../Controls/EncodeProjectionRatio.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #110A
                disp #D10A
                include "../Controls/ContinueProjectionRatio.asm"               ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1165
                disp #D165
                include "../Controls/DivideByteFraction.asm"                    ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1167
                disp #D167
                include "../Controls/DivideWordByByte.asm"                      ; (3) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #117D
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #D17D
                include "../Controls/Data/BodyProjection.asm"
                ent
                assert $ == #1181
                disp #D181
                include "../Controls/Data/CircleWork.asm"
                ent
                assert $ == #118D
                disp #D18D
                include "../Controls/DrawRightClippedHalfDown.asm"
                ent
                assert $ == #11A2
                disp #D1A2
                include "../Controls/DrawRightClippedHalfUp.asm"
                ent
                assert $ == #11B6
                disp #D1B6
                include "../Controls/DrawLeftClippedHalfDown.asm"
                ent
                assert $ == #11CB
                disp #D1CB
                include "../Controls/DrawLeftClippedHalfUp.asm"
                ent
                assert $ == #11DF
                disp #D1DF
                include "../Controls/DrawCircleHalfDown.asm"
                ent
                assert $ == #11F4
                disp #D1F4
                include "../Controls/DrawCircleHalfUp.asm"
                ent
                assert $ == #1208
                disp #D208
                include "../Controls/FillInteriorRowsUp.asm"
                ent
                assert $ == #1211
                disp #D211
                include "../Controls/FillInteriorRowsDown.asm"
                ent
                assert $ == #121A
                disp #D21A
                include "../Controls/DrawProjectedBody.asm"
                ent
                assert $ == #1227
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified005.bin"
                assert $ == #1232
                disp #D232
                include "../Controls/CallLargeCircle.asm"
                ent
                assert $ == #1236
                disp #D236
                include "../Controls/DrawLargeCircle.asm"
                ent
                assert $ == #130B
                disp #D30B
                include "../Controls/ReadByteSquare.asm"
                ent
                assert $ == #1314
                disp #D314
                include "../Controls/DrawInteriorCircle.asm"
                ent
                assert $ == #1320
                disp #D320
                include "../Controls/BuildCircleSpan.asm"
                ent
                assert $ == #1340
                disp #D340
                include "../Controls/DrawFullWidthCircle.asm"
                ent
                assert $ == #138C
                disp #D38C
                include "../Controls/DrawFullWidthCircleSlice.asm"
                ent
                assert $ == #13DA
                disp #D3DA
                include "../Controls/DrawHorizontallyClippedCircle.asm"
                ent
                assert $ == #1404
                disp #D404
                include "../Controls/DrawCornerCircleSlice.asm"
                ent
                assert $ == #1485
                disp #D485
                include "../Controls/DrawVerticalCircleSlice.asm"
                ent
                assert $ == #14CB
                disp #D4CB
                include "../Controls/PrepareCircleRightClip.asm"
                ent
                assert $ == #14E4
                disp #D4E4
                include "../Controls/PrepareCircleLeftClip.asm"
                ent
                assert $ == #1501
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified006.bin"
                assert $ == #1504
                disp #D504
                include "../Controls/LoadCircleMidpoint.asm"
                ent
                assert $ == #1515
                disp #D515
                include "../Controls/BuildLeftSpanMask.asm"
                ent
                assert $ == #153C
                disp #D53C
                include "../Controls/BuildRightSpanMask.asm"
                ent
                assert $ == #156C
                disp #D56C
                include "../Controls/LoadCircleClipState.asm"
                ent
                assert $ == #157B
                disp #D57B
                include "../Controls/PrepareInteriorSpan.asm"
                ent
                assert $ == #1609
                disp #D609
                include "../Controls/SqrtSquareDiff.asm"
                ent
                assert $ == #1633
                disp #D633
                include "../Controls/CircleRasterCore.asm"                      ; (0) жёсткий порядок, продолжение цепочки PUSH AF
                ent
                assert $ == #1727
                disp #D727
                include "../Controls/ResumeCirclePushSpan.asm"                  ; (1) жёсткий порядок, продолжение цепочки PUSH AF
                ent
                assert $ == #173B
                disp #D73B
                include "../Controls/LeftClippedCircleCore.asm"
                ent
                assert $ == #1833
                disp #D833
                include "../Controls/RightClippedCircleCore.asm"
                ent
                assert $ == #1925
                disp #D925
                include "../Controls/AdvanceRasterUp.asm"
                ent
                assert $ == #1940
                disp #D940
                include "../Controls/AdvanceRasterDown.asm"
                ent
                assert $ == #195B
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified010.bin"
                assert $ == #195F
                disp #D95F
                include "../Controls/ProjectAndCheckComponents.asm"
                ent
                assert $ == #197E
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #D97E
                include "../Controls/Data/SmallMaskSeeds.asm"
                ent
                assert $ == #1990
                disp #D990
                include "../Controls/Data/SmallMaskRows.asm"
                ent
                assert $ == #199C
                ; Unknown, назначение следующих 20 исходных байтов отдельно не установлено
                incbin "../Resources/22_CONTROL0/Unclassified011_AfterMasks.bin"
                assert $ == #19B0
                disp #D9B0
                include "../Controls/BuildSmallBodyMasks.asm"
                ent
                assert $ == #19DE
                disp #D9DE
                include "../Controls/DrawSmallBody.asm"
                ent
                assert $ == #1AB9
                disp #DAB9
                include "../Controls/CompareComponents.asm"
                ent
                assert $ == #1ADE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/22_CONTROL0/Unclassified012.bin"
                assert $ == #1B00
