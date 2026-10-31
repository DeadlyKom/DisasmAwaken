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
                incbin "../Resources/06_D3D/AfterSceneMatrix.bin"
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
                incbin "../Resources/06_D3D/AfterQueueStorage.bin"
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
                incbin "../Resources/06_D3D/AfterModelPointers.bin"
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
                incbin "../Resources/06_D3D/BeforeVertexClass.bin"
                assert $ == #1F46
                disp #DF46
                include "../D3D/ClassifyPreviewVertices.asm"
                ent
                assert $ == #1FA6
                incbin "../Resources/06_D3D/AfterVertexClass.bin"
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
                incbin "../Resources/06_D3D/BeforePreviewThird.bin"
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
                incbin "../Resources/06_D3D/BeforeCoordinateMultiply.bin"
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
                incbin "../Resources/06_D3D/BeforeModelMatrix.bin"
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
