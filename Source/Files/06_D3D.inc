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
                incbin "../Resources/06_D3D/AfterSquareTable.bin"
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
                incbin "../Resources/06_D3D/BeforeVertexGroup.bin"
                assert $ == #1908
                disp #D908
                include "../D3D/ProjectPreviewVertexGroup.asm"
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
                incbin "../Resources/06_D3D/AfterProjectionScale.bin"
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
                incbin "../Resources/06_D3D/AfterModelMatrix.bin"
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
