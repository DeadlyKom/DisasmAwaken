; -----------------------------------------
; запись 6, D3D.C
; логическая длина 15978, полный секторный размер 16128
; -----------------------------------------
                assert $ == #0000
                ; Unknown, исходные байты вне подтверждённого прямого потока управления
                incbin "../Resources/06_D3D/BeforeSceneSeed.bin"
                assert $ == #0200
                disp #C200
                include "../D3D/Data/PreviewSharedSeed.asm"
                ent
                assert $ == #0203
                incbin "../Resources/06_D3D/BetweenSceneSeedMatrix.bin"
                assert $ == #020C
                disp #C20C
                include "../D3D/Data/PreviewSceneMatrix.asm"
                ent
                assert $ == #021E
                disp #C21E
                include "../D3D/Data/PreviewObjectAngles.asm"
                ent
                assert $ == #0221
                incbin "../Resources/06_D3D/BeforeContourSizeAfterAngles.bin"
                assert $ == #022B
                assert $ == #022B
                disp #C22B
                include "../D3D/Data/PreviewContourSize.asm"
                ent
                assert $ == #022C
                disp #C22C
                include "../D3D/Data/PreviewClipFirst.asm"
                ent
                assert $ == #0231
                incbin "../Resources/06_D3D/AfterClipFirst.bin"
                assert $ == #023B
                assert $ == #023B
                disp #C23B
                include "../D3D/Data/PreviewFillMode.asm"
                ent
                assert $ == #023C
                disp #C23C
                include "../D3D/Data/PreviewClipSecond.asm"
                ent
                assert $ == #0241
                incbin "../Resources/06_D3D/AfterClipSecond.bin"
                assert $ == #024B
                assert $ == #024B
                assert $ == #024B
                disp #C24B
                include "../D3D/Data/PreviewEdgeEndpoints.asm"
                ent
                assert $ == #024F
                disp #C24F
                include "../D3D/Data/PreviewClipCorners.asm"
                ent
                assert $ == #0251
                incbin "../Resources/06_D3D/BeforeLineCoordinates.bin"
                assert $ == #025B
                disp #C25B
                include "../D3D/Data/PreviewLineCoordinates.asm"
                ent
                assert $ == #0261
                incbin "../Resources/06_D3D/BetweenLineWords.bin"
                assert $ == #026B
                disp #C26B
                include "../D3D/Data/PreviewLineTail.asm"
                ent
                assert $ == #026F
                assert $ == #026F
                assert $ == #026F
                disp #C26F
                include "../D3D/Data/PreviewEdgeMode.asm"
                ent
                assert $ == #0271
                incbin "../Resources/06_D3D/BeforeFaceGateState.bin"
                assert $ == #027B
                disp #C27B
                include "../D3D/Data/PreviewFaceGateState.asm"
                ent
                assert $ == #027C
                incbin "../Resources/06_D3D/BeforeClipProducts.bin"
                assert $ == #02DC
                disp #C2DC
                include "../D3D/Data/PreviewClipTopProduct.asm"
                ent
                assert $ == #02E0
                incbin "../Resources/06_D3D/BetweenClipTopBottom.bin"
                assert $ == #02EA
                disp #C2EA
                include "../D3D/Data/PreviewClipBottomProduct.asm"
                ent
                assert $ == #02EE
                disp #C2EE
                include "../D3D/Data/PreviewClipLeftLow.asm"
                ent
                assert $ == #02F0
                incbin "../Resources/06_D3D/BetweenClipLeftWords.bin"
                assert $ == #02FA
                disp #C2FA
                include "../D3D/Data/PreviewClipLeftHigh.asm"
                ent
                assert $ == #02FC
                disp #C2FC
                include "../D3D/Data/PreviewClipRightProduct.asm"
                ent
                assert $ == #0300
                assert $ == #0300
                assert $ == #0300
                assert $ == #0300
                assert $ == #0300
                disp #C300
                include "../D3D/Data/FoldedSquare127.asm"
                ent
                assert $ == #0400
                incbin "../Resources/06_D3D/BeforeProjectedVertices.bin"
                assert $ == #0600
                disp #C600
                include "../D3D/Data/PreviewProjectedVertices.asm"
                ent
                assert $ == #0700
                assert $ == #0700
                disp #C700
                include "../D3D/Data/PreviewQueue.asm"
                ent
                assert $ == #07FC
                incbin "../Resources/06_D3D/BeforePixelMasks.bin"
                assert $ == #0DB0
                disp #CDB0
                include "../D3D/Data/PreviewPixelMasks.asm"
                ent
                assert $ == #0DC0
                incbin "../Resources/06_D3D/BeforePrimaryAngles.bin"
                assert $ == #0DC7
                disp #CDC7
                include "../D3D/Data/PreviewPrimaryAngles.asm"
                ent
                assert $ == #0DCA
                incbin "../Resources/06_D3D/AfterPrimaryAngles.bin"
                assert $ == #0E40
                assert $ == #0E40
                assert $ == #0E40
                assert $ == #0E40
                disp #CE40
                include "../D3D/Data/PreviewPrices.asm"
                ent
                assert $ == #0EFA
                disp #CEFA
                include "../D3D/Data/PreviewDrawState.asm"
                ent
                assert $ == #0F04
                incbin "../Resources/06_D3D/AfterDrawState.bin"
                assert $ == #1000
                disp #D000
                include "../D3D/Data/PreviewModelPointers.asm"
                ent
                assert $ == #102C
                incbin "../Resources/06_D3D/BeforeFillPatterns.bin"
                assert $ == #1100
                disp #D100
                include "../D3D/Data/PreviewFillPatterns.asm"
                ent
                assert $ == #1110
                incbin "../Resources/06_D3D/AfterFillPatterns.bin"
                assert $ == #11C0
                assert $ == #11C0
                disp #D1C0
                include "../D3D/WritePreviewPolygonSpan.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1207
                disp #D207
                include "../D3D/StepPreviewPolygonRow.asm"                      ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1282
                disp #D282
                include "../D3D/SelectPreviewRightEdge.asm"
                ent
                assert $ == #1285
                disp #D285
                include "../D3D/WrapPreviewLeftEdge.asm"
                ent
                assert $ == #128C
                disp #D28C
                include "../D3D/UpdatePreviewLeftEdge.asm"
                ent
                assert $ == #134B
                disp #D34B
                include "../D3D/WrapPreviewRightEdge.asm"
                ent
                assert $ == #1350
                disp #D350
                include "../D3D/UpdatePreviewRightEdge.asm"
                ent
                assert $ == #140F
                disp #D40F
                include "../D3D/WrapPreviewTopLeft.asm"
                ent
                assert $ == #1416
                disp #D416
                include "../D3D/WrapPreviewTopRight.asm"
                ent
                assert $ == #141B
                disp #D41B
                include "../D3D/FillPreviewPolygon.asm"
                ent
                assert $ == #14DF
                assert $ == #14DF
                assert $ == #14DF
                assert $ == #14DF
                disp #D4DF
                include "../D3D/DividePreviewSlopeByte.asm"
                ent
                assert $ == #1518
                assert $ == #1518
                assert $ == #1518
                disp #D518
                include "../D3D/LookupPreviewProductE.asm"
                ent
                assert $ == #1525
                disp #D525
                include "../D3D/LookupPreviewProductB.asm"
                ent
                assert $ == #1532
                disp #D532
                include "../D3D/LookupPreviewProductC.asm"
                ent
                assert $ == #153F
                disp #D53F
                include "../D3D/LookupPreviewProductD.asm"
                ent
                assert $ == #154C
                disp #D54C
                include "../D3D/ComposePreviewMatrix.asm"
                ent
                assert $ == #1819
                disp #D819
                include "../D3D/ProjectPlanarModelGroups.asm"
                ent
                assert $ == #185E
                assert $ == #185E
                disp #D85E
                include "../D3D/ProjectPlanarVertexGroup.asm"
                ent
                assert $ == #1896
                disp #D896
                include "../D3D/ProjectPreviewModelGroups.asm"
                ent
                assert $ == #18BE
                assert $ == #18BE
                disp #D8BE
                include "../D3D/PreparePreviewVertexProducts.asm"               ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1908
                assert $ == #1908
                disp #D908
                include "../D3D/ProjectPreviewVertexGroup.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1A14
                assert $ == #1A14
                disp #DA14
                include "../D3D/ProjectPreviewVertex.asm"
                ent
                assert $ == #1BD9
                assert $ == #1BD9
                disp #DBD9
                include "../D3D/ConfigurePreviewProjectionScale.asm"
                ent
                assert $ == #1BE9
                disp #DBE9
                include "../D3D/RenderPreviewClippedFaces.asm"
                ent
                assert $ == #1D4F
                assert $ == #1D4F
                disp #DD4F
                include "../D3D/RenderPreviewInsideFaces.asm"
                ent
                assert $ == #1DFD
                assert $ == #1DFD
                disp #DDFD
                include "../D3D/CollectPreviewFaceCodes.asm"
                ent
                assert $ == #1E1C
                disp #DE1C
                include "../D3D/RasterizePreviewEdge.asm"
                ent
                assert $ == #1F46
                assert $ == #1F46
                assert $ == #1F46
                disp #DF46
                include "../D3D/ClassifyPreviewVertices.asm"
                ent
                assert $ == #1FA6
                disp #DFA6
                include "../D3D/ComputePreviewFaceOrientation.asm"
                ent
                assert $ == #2011
                assert $ == #2011
                assert $ == #2011
                assert $ == #2011
                assert $ == #2011
                assert $ == #2011
                assert $ == #2011
                disp #E011
                include "../D3D/ConfigurePreviewClip.asm"
                ent
                assert $ == #207F
                disp #E07F
                include "../D3D/RenderPreviewFrame.asm"
                ent
                assert $ == #20B5
                assert $ == #20B5
                disp #E0B5
                include "../D3D/AdjustPreviewThird.asm"
                ent
                assert $ == #20C5
                disp #E0C5
                include "../D3D/DrawPreviewPrices.asm"
                ent
                assert $ == #2124
                assert $ == #2124
                disp #E124
                include "../D3D/CountPreviewTextRows.asm"
                ent
                assert $ == #213C
                assert $ == #213C
                disp #E13C
                include "../D3D/SetupPreviewModel.asm"
                ent
                assert $ == #2154
                disp #E154
                include "../D3D/PrintPreviewTextRows.asm"
                ent
                assert $ == #2171
                disp #E171
                include "../D3D/ClipPreviewPolygon.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #21EB
                assert $ == #21EB
                disp #E1EB
                include "../D3D/PreviewClipCases.asm"                           ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #25E8
                assert $ == #25E8
                disp #E5E8
                include "../D3D/BuildPreviewClipTopProduct.asm"
                ent
                assert $ == #2607
                disp #E607
                include "../D3D/BuildPreviewClipBottomProduct.asm"
                ent
                assert $ == #2626
                disp #E626
                include "../D3D/BuildPreviewClipLeftProduct.asm"
                ent
                assert $ == #2645
                disp #E645
                include "../D3D/BuildPreviewClipRightProduct.asm"
                ent
                assert $ == #2664
                disp #E664
                include "../D3D/AppendPreviewClipTopIntersection.asm"
                ent
                assert $ == #26AF
                disp #E6AF
                include "../D3D/AppendPreviewClipBottomIntersection.asm"
                ent
                assert $ == #26FA
                disp #E6FA
                include "../D3D/AppendPreviewClipLeftIntersection.asm"
                ent
                assert $ == #2757
                disp #E757
                include "../D3D/AppendPreviewClipRightIntersection.asm"
                ent
                assert $ == #27B4
                assert $ == #27B4
                assert $ == #27B4
                disp #E7B4
                include "../D3D/AppendPreviewClipTopLeft.asm"
                ent
                assert $ == #27BF
                disp #E7BF
                include "../D3D/AppendPreviewClipTopRight.asm"
                ent
                assert $ == #27CA
                disp #E7CA
                include "../D3D/AppendPreviewClipBottomLeft.asm"
                ent
                assert $ == #27D5
                disp #E7D5
                include "../D3D/AppendPreviewClipBottomRight.asm"
                ent
                assert $ == #27E0
                disp #E7E0
                include "../D3D/SubtractPreviewClipTopLeft.asm"
                ent
                assert $ == #27F4
                disp #E7F4
                include "../D3D/SubtractPreviewClipTopRight.asm"
                ent
                assert $ == #2808
                disp #E808
                include "../D3D/SubtractPreviewClipBottomLeft.asm"
                ent
                assert $ == #281C
                disp #E81C
                include "../D3D/SubtractPreviewClipBottomRight.asm"
                ent
                assert $ == #2830
                assert $ == #2830
                disp #E830
                include "../D3D/SubtractPreviewClipColumns.asm"
                ent
                assert $ == #283B
                disp #E83B
                include "../D3D/SubtractPreviewClipRows.asm"
                ent
                assert $ == #2846
                disp #E846
                include "../D3D/AppendPreviewClipSecond.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #284E
                disp #E84E
                include "../D3D/AppendPreviewClipPoint.asm"                     ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #285D
                assert $ == #285D
                disp #E85D
                include "../D3D/UnwindPreviewClipFrame.asm"
                ent
                assert $ == #2867
                incbin "../Resources/06_D3D/BeforeFaceProduct.bin"
                assert $ == #2869
                assert $ == #2869
                disp #E869
                include "../D3D/MultiplyPreviewSignedWords.asm"
                ent
                assert $ == #2A01
                disp #EA01
                include "../D3D/DividePreviewClip32To16.asm"
                ent
                assert $ == #2AB6
                disp #EAB6
                include "../D3D/DispatchPreviewClipSegment.asm"
                ent
                assert $ == #2B10
                assert $ == #2B10
                assert $ == #2B10
                assert $ == #2B10
                disp #EB10
                include "../D3D/MultiplyPreviewCoordinate.asm"
                ent
                assert $ == #2B7E
                disp #EB7E
                include "../D3D/TransformPreviewCoords.asm"
                ent
                assert $ == #2C28
                disp #EC28
                include "../D3D/BuildPreviewQueue.asm"                          ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2DB0
                assert $ == #2DB0
                disp #EDB0
                include "../D3D/CheckPreviewBounds.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2E24
                assert $ == #2E24
                disp #EE24
                include "../D3D/InsertPreviewQueue.asm"                         ; (2) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2EEE
                disp #EEEE
                include "../D3D/RestorePreviewStack.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2EF1
                disp #EEF1
                include "../D3D/RenderPreviewQueue.asm"                         ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #2F5E
                assert $ == #2F5E
                disp #EF5E
                include "../D3D/BuildPreviewModelMatrix.asm"
                ent
                assert $ == #3056
                disp #F056
                include "../D3D/Data/ModelGroups/Orsan.asm"
                ent
                assert $ == #306D
                incbin "../Resources/06_D3D/AfterOrsanGroups.bin"
                assert $ == #30F6
                disp #F0F6
                include "../D3D/Data/ModelGroups/Memfis.asm"
                ent
                assert $ == #3109
                incbin "../Resources/06_D3D/AfterMemfisGroups.bin"
                assert $ == #3163
                disp #F163
                include "../D3D/Data/ModelGroups/Dominion.asm"
                ent
                assert $ == #3192
                incbin "../Resources/06_D3D/AfterDominionGroups.bin"
                assert $ == #31F6
                disp #F1F6
                include "../D3D/Data/ModelGroups/Baros.asm"
                ent
                assert $ == #320D
                incbin "../Resources/06_D3D/AfterBarosGroups.bin"
                assert $ == #3271
                disp #F271
                include "../D3D/Data/ModelGroups/Firs.asm"
                ent
                assert $ == #328C
                incbin "../Resources/06_D3D/AfterFirsGroups.bin"
                assert $ == #32C0
                disp #F2C0
                include "../D3D/Data/ModelGroups/Sofist.asm"
                ent
                assert $ == #32E3
                incbin "../Resources/06_D3D/AfterSofistGroups.bin"
                assert $ == #333F
                disp #F33F
                include "../D3D/Data/ModelGroups/Kridon.asm"
                ent
                assert $ == #3356
                incbin "../Resources/06_D3D/AfterKridonGroups.bin"
                assert $ == #33AB
                disp #F3AB
                include "../D3D/Data/ModelGroups/Algol.asm"
                ent
                assert $ == #33CA
                incbin "../Resources/06_D3D/AfterAlgolGroups.bin"
                assert $ == #3467
                disp #F467
                include "../D3D/Data/ModelGroups/Protos.asm"
                ent
                assert $ == #347A
                incbin "../Resources/06_D3D/AfterProtosGroups.bin"
                assert $ == #34D1
                disp #F4D1
                include "../D3D/Data/ModelGroups/Fervest.asm"
                ent
                assert $ == #34F0
                incbin "../Resources/06_D3D/AfterFervestGroups.bin"
                assert $ == #3581
                assert $ == #3581
                assert $ == #3581
                assert $ == #3581
                assert $ == #3581
                assert $ == #3581
                disp #F581
                include "../D3D/Data/ShipDescriptions.asm"
                ent
                assert $ == #3BD8
                disp #FBD8
                include "../D3D/Data/SkimmerDescriptions.asm"
                ent
                assert $ == #3E6A
                incbin "../Resources/06_D3D/AfterDescriptionText.bin"
                assert $ == #3F00
                assert $ == #3F00
