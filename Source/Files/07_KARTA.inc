; -----------------------------------------
; запись 7, KARTA.C
; логическая длина 11776, полный секторный размер 11776
; -----------------------------------------
                assert $ == #0000
                disp #C000
                include "../Map/DrawMapScene.asm"
                ent
                assert $ == #0231
                disp #C231
                include "../Map/XorMapPointMarker.asm"
                ent
                assert $ == #0325
                disp #C325
                include "../Map/SelectMapPoint.asm"                             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0333
                disp #C333
                include "../Map/CenterMapView.asm"                              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0368
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #C368
                include "../Map/SumSquares8.asm"
                ent
                assert $ == #038C
                disp #C38C
                include "../Map/SelectNearestVisiblePoint.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #040F
                assert $ == #040F
                disp #C40F
                include "../Map/ReadStoredMapVariant.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #044A
                disp #C44A
                include "../Map/BuildMapQuadrantTables.asm"
                ent
                assert $ == #0474
                disp #C474
                include "../Map/BuildMapSectorTable.asm"
                ent
                assert $ == #049B
                assert $ == #049B
                disp #C49B
                include "../Map/BuildMapScreenTables.asm"
                ent
                assert $ == #04E5
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #C4E5
                include "../Map/BuildVisibleMapPoints.asm"
                ent
                assert $ == #05E8
                disp #C5E8
                include "../Map/SelectNearestMapVariant.asm"
                ent
                assert $ == #0653
                disp #C653
                include "../Map/UpdateMapDistanceMinimum.asm"
                ent
                assert $ == #0677
                ; Unknown, сохранённые байты вне новых доказанных входов
                disp #C677
                include "../Map/DrawVariantCluster.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06C0
                disp #C6C0
                include "../Map/AnimateVariant0.asm"                            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06DD
                disp #C6DD
                include "../Map/AnimateVariant1.asm"                            ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #06FA
                disp #C6FA
                include "../Map/AnimateVariant2.asm"                            ; (3) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0717
                disp #C717
                include "../Map/AnimateVariant3.asm"                            ; (4) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0734
                disp #C734
                include "../Map/AnimateVariant4.asm"                            ; (5) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0751
                disp #C751
                include "../Map/AnimateVariant5.asm"                            ; (6) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #076E
                disp #C76E
                include "../Map/SelectBlinkingVariant.asm"
                ent
                assert $ == #0781
                assert $ == #0781
                assert $ == #0781
                disp #C781
                include "../Map/PrepareVariantResources.asm"
                ent
                assert $ == #07B4
                disp #C7B4
                include "../Map/SelectVariantResource.asm"
                ent
                assert $ == #0827
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                disp #C827
                include "../Map/XorVariantPhase.asm"
                ent
                assert $ == #088F
                assert $ == #088F
                disp #C88F
                include "../Map/FindSecondaryMapPoint.asm"
                ent
                assert $ == #0894
                disp #C894
                include "../Map/FindStoredMapPoint.asm"
                ent
                assert $ == #08C2
                disp #C8C2
                include "../Map/PrintSelectedVariantLabel.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #08C9
                disp #C8C9
                include "../Map/PrintVariantLabel.asm"                          ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0908
                disp #C908
                include "../Map/XorSelectionBand.asm"
                ent
                assert $ == #09B9
                disp #C9B9
                include "../Map/DescribeKey.asm"
                ent
                assert $ == #09FB
                disp #C9FB
                include "../Map/RefreshSecondaryPointOrder.asm"
                ent
                assert $ == #0A45
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                ; Unknown, сохранённые байты вне новых доказанных входов
                disp #CA45
                include "../Map/Data/VariantPath7.asm"
                ent
                assert $ == #0A7E
                disp #CA7E
                include "../Map/Data/VariantPath10.asm"
                ent
                assert $ == #0ACF
                disp #CACF
                include "../Map/Data/VariantPath13.asm"
                ent
                assert $ == #0B38
                disp #CB38
                include "../Map/Data/VariantPath16.asm"
                ent
                assert $ == #0BB9
                disp #CBB9
                include "../Map/Data/VariantPath19.asm"
                ent
                assert $ == #0C52
                disp #CC52
                include "../Map/Data/VariantPath22.asm"
                ent
                assert $ == #0D03
                disp #CD03
                include "../Map/Resources/VariantDefault.asm"
                ent
                assert $ == #0D33
                disp #CD33
                include "../Map/Resources/VariantCurrent.asm"
                ent
                assert $ == #0D63
                disp #CD63
                include "../Map/Resources/VariantStored.asm"
                ent
                assert $ == #0D93
                disp #CD93
                include "../Map/Resources/VariantSelected.asm"
                ent
                assert $ == #0DC3
                assert $ == #0DC3
                disp #CDC3
                include "../Map/Resources/MarkerSelected.asm"
                ent
                assert $ == #0E43
                disp #CE43
                include "../Map/Resources/MarkerSecondary.asm"
                ent
                assert $ == #0EC3
                disp #CEC3
                include "../Map/Resources/MarkerActiveAux.asm"
                ent
                assert $ == #0F43
                disp #CF43
                include "../Map/Resources/MarkerCursor.asm"
                ent
                assert $ == #0FC3
                disp #CFC3
                include "../Map/Resources/MarkerPrimary.asm"
                ent
                assert $ == #1043
                disp #D043
                include "../Map/Resources/MarkerStored.asm"
                ent
                assert $ == #10C3
                assert $ == #10C3
                disp #D0C3
                include "../Map/SetupMapRasterWindow.asm"
                ent
                assert $ == #11AC
                assert $ == #11AC
                disp #D1AC
                include "../Map/DrawMapPointChain.asm"
                ent
                assert $ == #12EE
                disp #D2EE
                include "../Map/RasterizeMapLine.asm"
                ent
                assert $ == #1418
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/07_KARTA/BeforeMapLineMasks.bin"
                assert $ == #1420
                disp #D420
                include "../Map/Data/MapLineMasks.asm"
                ent
                assert $ == #1430
                assert $ == #1430
                disp #D430
                include "../Map/BuildMapPointOutcodes.asm"
                ent
                assert $ == #148B
                disp #D48B
                include "../Map/DispatchMapClipEdge.asm"
                ent
                assert $ == #14DD
                ; доказанные корни косвенной таблицы, семантический разбор входов продолжается
                disp #D4DD
                include "../Map/MapClipCases.asm"
                ent
                assert $ == #18E2
                disp #D8E2
                include "../Map/ComputeTopClipProduct.asm"
                ent
                assert $ == #1901
                disp #D901
                include "../Map/ComputeBottomClipProduct.asm"
                ent
                assert $ == #1920
                disp #D920
                include "../Map/ComputeLeftClipProduct.asm"
                ent
                assert $ == #193F
                disp #D93F
                include "../Map/ComputeRightClipProduct.asm"
                ent
                assert $ == #195E
                disp #D95E
                include "../Map/AppendTopClipIntersection.asm"
                ent
                assert $ == #19A9
                disp #D9A9
                include "../Map/AppendBottomClipIntersection.asm"
                ent
                assert $ == #19F4
                disp #D9F4
                include "../Map/AppendLeftClipIntersection.asm"
                ent
                assert $ == #1A52
                disp #DA52
                include "../Map/AppendRightClipIntersection.asm"
                ent
                assert $ == #1AB0
                disp #DAB0
                include "../Map/AppendTopLeftCorner.asm"
                ent
                assert $ == #1ABB
                disp #DABB
                include "../Map/AppendTopRightCorner.asm"
                ent
                assert $ == #1AC6
                disp #DAC6
                include "../Map/AppendBottomLeftCorner.asm"
                ent
                assert $ == #1AD1
                disp #DAD1
                include "../Map/AppendBottomRightCorner.asm"
                ent
                assert $ == #1ADC
                disp #DADC
                include "../Map/SubtractTopLeftProducts.asm"
                ent
                assert $ == #1AF0
                disp #DAF0
                include "../Map/SubtractTopRightProducts.asm"
                ent
                assert $ == #1B04
                disp #DB04
                include "../Map/SubtractBottomLeftProducts.asm"
                ent
                assert $ == #1B18
                disp #DB18
                include "../Map/SubtractBottomRightProducts.asm"
                ent
                assert $ == #1B2C
                disp #DB2C
                include "../Map/SubtractClipPointX.asm"
                ent
                assert $ == #1B37
                disp #DB37
                include "../Map/SubtractClipPointY.asm"
                ent
                assert $ == #1B42
                disp #DB42
                include "../Map/AppendSecondClipPoint.asm"
                ent
                assert $ == #1B59
                disp #DB59
                include "../Map/UnwindClipFrame.asm"
                ent
                assert $ == #1B63
                assert $ == #1B63
                assert $ == #1B63
                assert $ == #1B63
                disp #DB63
                include "../Map/MultiplySigned16.asm"
                ent
                assert $ == #1CFB
                disp #DCFB
                include "../Map/DivideSigned32To16.asm"
                ent
                assert $ == #1DB0
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/07_KARTA/BeforeMapChainPoints.bin"
                assert $ == #1E0B
                disp #DE0B
                include "../Map/Data/CurrentMapChainPoint.asm"
                ent
                assert $ == #1E10
                incbin "../Resources/07_KARTA/BetweenMapChainPoints.bin"
                assert $ == #1E1B
                disp #DE1B
                include "../Map/Data/PreviousMapChainPoint.asm"
                ent
                assert $ == #1E20
                incbin "../Resources/07_KARTA/AfterMapChainPoints.bin"
                assert $ == #1E2B
                assert $ == #1E2B
                disp #DE2B
                include "../Map/Data/MapLinePoints.asm"
                ent
                assert $ == #1E2F
                assert $ == #1E2F
                disp #DE2F
                include "../Map/Data/ClipEndpoints.asm"
                ent
                assert $ == #1E39
                disp #DE39
                include "../Map/Data/ClipCornerState.asm"
                ent
                assert $ == #1E3B
                disp #DE3B
                include "../Map/Data/ClipOutputSize.asm"
                ent
                assert $ == #1E3C
                disp #DE3C
                include "../Map/Data/MapLineMode.asm"
                ent
                assert $ == #1E3E
                incbin "../Resources/07_KARTA/AfterMapLineMode.bin"
                assert $ == #1E6B
                assert $ == #1E6B
                disp #DE6B
                include "../Map/Data/ClipProducts.asm"
                ent
                assert $ == #1E7B
                incbin "../Resources/07_KARTA/BeforeArcWorkspace.bin"
                assert $ == #1FAB
                disp #DFAB
                include "../Map/Data/ArcWorkspace.asm"
                ent
                assert $ == #1FC3
                assert $ == #1FC3
                assert $ == #1FC3
                disp #DFC3
                include "../Map/DrawClippedMapArc.asm"
                ent
                assert $ == #2208
                disp #E208
                include "../Map/PrepareArcFullSpan.asm"
                ent
                assert $ == #2228
                disp #E228
                include "../Map/DrawClippedArcPair.asm"
                ent
                assert $ == #2248
                assert $ == #2248
                disp #E248
                include "../Map/PrepareArcLeftEdge.asm"
                ent
                assert $ == #2260
                disp #E260
                include "../Map/PrepareArcRightEdge.asm"
                ent
                assert $ == #2278
                disp #E278
                include "../Map/LoadArcRasterInputs.asm"
                ent
                assert $ == #2289
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/07_KARTA/Unclassified008.bin"
                assert $ == #2299
                disp #E299
                include "../Map/LoadClippedArcInputs.asm"
                ent
                assert $ == #22AB
                disp #E2AB
                include "../Map/RasterizeArcEdges.asm"
                ent
                assert $ == #2514
                assert $ == #2514
                disp #E514
                include "../Map/PrepareLeftRasterPoint.asm"
                ent
                assert $ == #252E
                disp #E52E
                include "../Map/PrepareRightRasterPoint.asm"
                ent
                assert $ == #2554
                disp #E554
                include "../Map/SqrtSquareDiff.asm"
                ent
                assert $ == #257E
                disp #E57E
                include "../Map/PreviousRasterRow.asm"
                ent
                assert $ == #25AC
                disp #E5AC
                include "../Map/NextRasterRow.asm"
                ent
                assert $ == #25D8
                disp #E5D8
                include "../Map/ResetRasterSpanEdges.asm"
                ent
                assert $ == #25E3
                disp #E5E3
                include "../Map/SeekRasterRowUp.asm"
                ent
                assert $ == #2621
                disp #E621
                include "../Map/SeekRasterRowDown.asm"
                ent
                assert $ == #265D
                disp #E65D
                include "../Map/LookupSquare.asm"
                ent
                assert $ == #2666
                disp #E666
                include "../Map/ResetRasterDown.asm"
                ent
                assert $ == #2674
                disp #E674
                include "../Map/ResetRasterUp.asm"
                ent
                assert $ == #2681
                disp #E681
                include "../Map/DrawArcLeftDown.asm"
                ent
                assert $ == #2688
                disp #E688
                include "../Map/DrawArcLeftUp.asm"
                ent
                assert $ == #268F
                disp #E68F
                include "../Map/DrawArcRightDown.asm"
                ent
                assert $ == #2696
                disp #E696
                include "../Map/DrawArcRightUp.asm"
                ent
                assert $ == #269D
                disp #E69D
                include "../Map/DrawArcBothDown.asm"
                ent
                assert $ == #26A4
                disp #E6A4
                include "../Map/DrawArcBothUp.asm"
                ent
                assert $ == #26AB
                disp #E6AB
                include "../Map/BuildSystemName.asm"
                ent
                assert $ == #26F6
                disp #E6F6
                include "../Map/AppendCompactDecimal.asm"
                ent
                assert $ == #2721
                ; начальный LF и шестнадцать префиксов имени системы
                disp #E721
                include "../Map/Data/SystemPrefixes.asm"
                ent
                assert $ == #2779
                disp #E779
                include "../Map/ClassifyKeyRegion.asm"
                ent
                assert $ == #27BA
                disp #E7BA
                include "../Map/MeasureCoordinateDistance.asm"
                ent
                assert $ == #2838
                disp #E838
                include "../Map/SeededSqrt16.asm"
                ent
                assert $ == #28BE
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/07_KARTA/Unclassified010.bin"
                assert $ == #2900
                ; таблица квадратов, 256 младших и 256 старших байтов
                incbin "../Map/Resources/Squares.bin"
                assert $ == #2B00
                ; страницы EB, EC, ED начального приближения, см. ../../Docs/SeededRoot.md
                incbin "../Map/Resources/RootSeeds.bin"
                assert $ == #2E00
