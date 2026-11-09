; -----------------------------------------
; запись 19, 3DPART.C
; логическая длина 8224, полный секторный размер 8448
; -----------------------------------------
                assert $ == #0000
                disp #C000
                include "../ThreeD/ClipPolygon.asm"
                ent
                assert $ == #0071
                disp #C071
                include "../ThreeD/ContinueClipPolygon.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007A
                disp #C07A
                include "../ThreeD/ReturnClipCase.asm"                          ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #007B
                disp #C07B
                include "../ThreeD/ClipInsideToBottomRight.asm"                 ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #008A
                disp #C08A
                include "../ThreeD/ClipRightToBottomRight.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0095
                disp #C095
                include "../ThreeD/ClipInsideToBottomLeft.asm"                  ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00A4
                disp #C0A4
                include "../ThreeD/ClipBottomToBottomLeft.asm"                  ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00AF
                disp #C0AF
                include "../ThreeD/ClipInsideToTopRight.asm"                    ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00BE
                disp #C0BE
                include "../ThreeD/ClipTopToTopRight.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00C9
                disp #C0C9
                include "../ThreeD/ClipInsideToTopLeft.asm"                     ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00D8
                disp #C0D8
                include "../ThreeD/ClipLeftToTopLeft.asm"                       ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #00E3
                disp #C0E3
                include "../ThreeD/ClipRightToInside.asm"
                ent
                assert $ == #00E9
                disp #C0E9
                include "../ThreeD/ClipRightToLeft.asm"
                ent
                assert $ == #00EF
                disp #C0EF
                include "../ThreeD/ClipRightToBottom.asm"
                ent
                assert $ == #0101
                disp #C101
                include "../ThreeD/ClipRightToBottomLeft.asm"
                ent
                assert $ == #0119
                disp #C119
                include "../ThreeD/ClipRightToTop.asm"
                ent
                assert $ == #012B
                disp #C12B
                include "../ThreeD/ClipRightToTopRight.asm"
                ent
                assert $ == #0132
                disp #C132
                include "../ThreeD/ClipRightToTopLeft.asm"
                ent
                assert $ == #0144
                disp #C144
                include "../ThreeD/ClipLeftToInside.asm"
                ent
                assert $ == #014A
                disp #C14A
                include "../ThreeD/ClipLeftToRight.asm"
                ent
                assert $ == #0150
                disp #C150
                include "../ThreeD/ClipLeftToBottom.asm"
                ent
                assert $ == #0162
                disp #C162
                include "../ThreeD/ClipLeftToBottomRight.asm"
                ent
                assert $ == #0174
                disp #C174
                include "../ThreeD/ClipLeftToBottomLeft.asm"
                ent
                assert $ == #017B
                disp #C17B
                include "../ThreeD/ClipLeftToTop.asm"
                ent
                assert $ == #018D
                disp #C18D
                include "../ThreeD/ClipLeftToTopRight.asm"
                ent
                assert $ == #01A5
                disp #C1A5
                include "../ThreeD/ClipBottomToInside.asm"
                ent
                assert $ == #01AB
                disp #C1AB
                include "../ThreeD/ClipBottomToRight.asm"
                ent
                assert $ == #01BD
                disp #C1BD
                include "../ThreeD/ClipBottomToLeft.asm"
                ent
                assert $ == #01CF
                disp #C1CF
                include "../ThreeD/ClipBottomToBottomRight.asm"
                ent
                assert $ == #01D6
                disp #C1D6
                include "../ThreeD/ClipBottomToTop.asm"
                ent
                assert $ == #01DC
                disp #C1DC
                include "../ThreeD/ClipBottomToTopRight.asm"
                ent
                assert $ == #01F1
                disp #C1F1
                include "../ThreeD/ClipBottomToTopLeft.asm"
                ent
                assert $ == #020C
                disp #C20C
                include "../ThreeD/ClipBottomRightToInside.asm"
                ent
                assert $ == #0228
                disp #C228
                include "../ThreeD/ClipBottomRightToRight.asm"
                ent
                assert $ == #022F
                disp #C22F
                include "../ThreeD/ClipBottomRightToLeft.asm"
                ent
                assert $ == #024E
                disp #C24E
                include "../ThreeD/ClipBottomRightToBottom.asm"
                ent
                assert $ == #0259
                disp #C259
                include "../ThreeD/ClipBottomRightToBottomLeft.asm"
                ent
                assert $ == #025F
                disp #C25F
                include "../ThreeD/ClipBottomRightToTop.asm"
                ent
                assert $ == #0274
                disp #C274
                include "../ThreeD/ClipBottomRightToTopLeft.asm"
                ent
                assert $ == #028D
                disp #C28D
                include "../ThreeD/ClipBottomLeftToInside.asm"
                ent
                assert $ == #02A9
                disp #C2A9
                include "../ThreeD/ClipBottomLeftToRight.asm"
                ent
                assert $ == #02BE
                disp #C2BE
                include "../ThreeD/ClipBottomLeftToLeft.asm"
                ent
                assert $ == #02C9
                disp #C2C9
                include "../ThreeD/ClipBottomLeftToBottom.asm"
                ent
                assert $ == #02D0
                disp #C2D0
                include "../ThreeD/ClipBottomLeftToTop.asm"
                ent
                assert $ == #02EF
                disp #C2EF
                include "../ThreeD/ClipBottomLeftToTopRight.asm"
                ent
                assert $ == #0308
                disp #C308
                include "../ThreeD/ClipBottomLeftToTopLeft.asm"
                ent
                assert $ == #030E
                disp #C30E
                include "../ThreeD/ClipTopToInside.asm"
                ent
                assert $ == #0314
                disp #C314
                include "../ThreeD/ClipTopToRight.asm"
                ent
                assert $ == #0326
                disp #C326
                include "../ThreeD/ClipTopToLeft.asm"
                ent
                assert $ == #0338
                disp #C338
                include "../ThreeD/ClipTopToBottom.asm"
                ent
                assert $ == #033E
                disp #C33E
                include "../ThreeD/ClipTopToBottomRight.asm"
                ent
                assert $ == #0359
                disp #C359
                include "../ThreeD/ClipTopToBottomLeft.asm"
                ent
                assert $ == #036E
                disp #C36E
                include "../ThreeD/ClipTopToTopLeft.asm"
                ent
                assert $ == #0375
                disp #C375
                include "../ThreeD/ClipTopRightToInside.asm"
                ent
                assert $ == #0391
                disp #C391
                include "../ThreeD/ClipTopRightToRight.asm"
                ent
                assert $ == #039C
                disp #C39C
                include "../ThreeD/ClipTopRightToLeft.asm"
                ent
                assert $ == #03B1
                disp #C3B1
                include "../ThreeD/ClipTopRightToBottom.asm"
                ent
                assert $ == #03D0
                disp #C3D0
                include "../ThreeD/ClipTopRightToBottomRight.asm"
                ent
                assert $ == #03D6
                disp #C3D6
                include "../ThreeD/ClipTopRightToBottomLeft.asm"
                ent
                assert $ == #03EF
                disp #C3EF
                include "../ThreeD/ClipTopRightToTop.asm"
                ent
                assert $ == #03F6
                disp #C3F6
                include "../ThreeD/ClipTopLeftToInside.asm"
                ent
                assert $ == #0412
                disp #C412
                include "../ThreeD/ClipTopLeftToRight.asm"
                ent
                assert $ == #0431
                disp #C431
                include "../ThreeD/ClipTopLeftToLeft.asm"
                ent
                assert $ == #0438
                disp #C438
                include "../ThreeD/ClipTopLeftToBottom.asm"
                ent
                assert $ == #044D
                disp #C44D
                include "../ThreeD/ClipTopLeftToBottomRight.asm"
                ent
                assert $ == #0466
                disp #C466
                include "../ThreeD/ClipTopLeftToTop.asm"
                ent
                assert $ == #0471
                disp #C471
                include "../ThreeD/ClipTopLeftToTopRight.asm"
                ent
                assert $ == #0477
                disp #C477
                include "../ThreeD/ComputeTopClipProduct.asm"
                ent
                assert $ == #0496
                disp #C496
                include "../ThreeD/ComputeBottomClipProduct.asm"
                ent
                assert $ == #04B5
                disp #C4B5
                include "../ThreeD/ComputeLeftClipProduct.asm"
                ent
                assert $ == #04D4
                disp #C4D4
                include "../ThreeD/ComputeRightClipProduct.asm"
                ent
                assert $ == #04F3
                disp #C4F3
                include "../ThreeD/ClipInsideToTop.asm"                         ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #04F6
                disp #C4F6
                include "../ThreeD/AppendTopClipIntersection.asm"               ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #053D
                disp #C53D
                include "../ThreeD/ClipInsideToBottom.asm"                      ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0540
                disp #C540
                include "../ThreeD/AppendBottomClipIntersection.asm"            ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0588
                disp #C588
                include "../ThreeD/ClipInsideToLeft.asm"                        ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #058B
                disp #C58B
                include "../ThreeD/AppendLeftClipIntersection.asm"              ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05E4
                disp #C5E4
                include "../ThreeD/ClipInsideToRight.asm"                       ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #05E7
                disp #C5E7
                include "../ThreeD/AppendRightClipIntersection.asm"             ; (1) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #0641
                disp #C641
                include "../ThreeD/AppendTopLeftClipCorner.asm"
                ent
                assert $ == #064C
                disp #C64C
                include "../ThreeD/AppendTopRightClipCorner.asm"
                ent
                assert $ == #0657
                disp #C657
                include "../ThreeD/AppendBottomLeftClipCorner.asm"
                ent
                assert $ == #0662
                disp #C662
                include "../ThreeD/AppendBottomRightClipCorner.asm"
                ent
                assert $ == #066D
                disp #C66D
                include "../ThreeD/CompareTopLeftProducts.asm"
                ent
                assert $ == #0681
                disp #C681
                include "../ThreeD/CompareTopRightProducts.asm"
                ent
                assert $ == #0695
                disp #C695
                include "../ThreeD/CompareBottomLeftProducts.asm"
                ent
                assert $ == #06A9
                disp #C6A9
                include "../ThreeD/CompareBottomRightProducts.asm"
                ent
                assert $ == #06BD
                disp #C6BD
                include "../ThreeD/ComputeSecondAxisDelta.asm"
                ent
                assert $ == #06C8
                disp #C6C8
                include "../ThreeD/ComputeFirstAxisDelta.asm"
                ent
                assert $ == #06D3
                disp #C6D3
                include "../ThreeD/AppendSecondClipPoint.asm"
                ent
                assert $ == #06EA
                disp #C6EA
                include "../ThreeD/ExitClipContour.asm"
                ent
                assert $ == #06F4
                disp #C6F4
                include "../ThreeD/MultiplySigned16.asm"
                ent
                assert $ == #088C
                disp #C88C
                include "../ThreeD/DivideSigned32To16.asm"
                ent
                assert $ == #0941
                disp #C941
                include "../ThreeD/ClipSingleEdge.asm"
                ent
                assert $ == #099B
                disp #C99B
                include "../ThreeD/BuildRenderCoefficients.asm"
                ent
                assert $ == #0B23
                disp #CB23
                include "../ThreeD/ComposeRenderMatrix.asm"
                ent
                assert $ == #0EE3
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                incbin "../Resources/19_3DPART/Unclassified0EE3_0F00.bin"
                assert $ == #0F00
                ; Документация [префикс таблицы и два рабочих байта](../../Docs/ClipDispatchPrefixData.md)
                disp #CF00
                include "../ThreeD/Data/ClipDispatchPrefix.asm"
                ent
                assert $ == #0F08
                disp #CF08
                include "../ThreeD/UnknownCF08.asm"
                ent
                assert $ == #0F0B
                disp #CF0B
                include "../ThreeD/Data/ClipFirstPoint.asm"
                ent
                assert $ == #0F10
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #0F10
                disp #CF10
                include "../ThreeD/Data/ClipTargetLowRow1.asm"
                ent
                assert $ == #0F1B
                disp #CF1B
                include "../ThreeD/Data/ClipSecondPoint.asm"
                ent
                assert $ == #0F20
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #0F20
                disp #CF20
                include "../ThreeD/Data/ClipTargetLowRow2.asm"
                ent
                assert $ == #0F2B
                disp #CF2B
                include "../ThreeD/Data/ClipProducts.asm"
                ent
                assert $ == #0F3B
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                ; Документация [таблицы и сохранённые промежутки](../../Docs/PolygonFillPhysicalData.md)
                assert $ == #0F3B
                ; Unknown, соседние байты не объявляются свободными
                ; Документация [таблицы и сохранённые промежутки](../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #0F3B
                disp #CF3B
                include "../ThreeD/Data/ClipTargetLowTail3.asm"
                ent
                assert $ == #0F40
                disp #CF40
                include "../ThreeD/Data/ClipTargetLowRows4F.asm"
                ent
                assert $ == #1000
                disp #D000
                include "../ThreeD/Data/ClipTargetHigh.asm"
                ent
                assert $ == #1100
                disp #D100
                include "../ThreeD/Data/PolygonPatterns.asm"
                ent
                assert $ == #110A
                disp #D10A
                include "../ThreeD/ClearWorkBuffer.asm"
                ent
                assert $ == #112C
                disp #D12C
                include "../ThreeD/MultiplySignedScaled.asm"
                ent
                assert $ == #1194
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                incbin "../Resources/19_3DPART/Physical1194.bin"
                assert $ == #11C0
                disp #D1C0
                include "../ThreeD/PolygonFillRows.asm"
                ent
                assert $ == #1268
                disp #D268
                include "../ThreeD/SelectPolygonRightEdge.asm"
                ent
                assert $ == #126B
                disp #D26B
                include "../ThreeD/WrapPolygonLeftEdge.asm"
                ent
                assert $ == #1272
                disp #D272
                include "../ThreeD/UpdatePolygonLeftEdge.asm"
                ent
                assert $ == #13A8
                disp #D3A8
                include "../ThreeD/WrapPolygonRightEdge.asm"
                ent
                assert $ == #13AD
                disp #D3AD
                include "../ThreeD/UpdatePolygonRightEdge.asm"                  ; (0) жёсткий порядок, отрицательный длинный путь продолжается в (1)
                ent
                assert $ == #14C1
                disp #D4C1
                include "../ThreeD/SelectPolygonRowLimit.asm"                   ; (1) жёсткий порядок, общий хвост после (0)
                ent
                assert $ == #14F5
                disp #D4F5
                include "../ThreeD/SetShortNegativeRightStep.asm"
                ent
                assert $ == #1503
                disp #D503
                include "../ThreeD/WrapPolygonLeftTop.asm"
                ent
                assert $ == #150A
                disp #D50A
                include "../ThreeD/WrapPolygonRightTop.asm"
                ent
                assert $ == #150F
                disp #D50F
                include "../ThreeD/ReturnPolygonFill.asm"
                ent
                assert $ == #1511
                disp #D511
                include "../ThreeD/PreparePolygonFill.asm"
                ent
                assert $ == #15C9
                disp #D5C9
                include "../ThreeD/TransformObjectVertices.asm"
                ent
                assert $ == #15F9
                disp #D5F9
                include "../ThreeD/PrepareRenderVertexProducts.asm"             ; (0) жёсткий порядок, последовательное исполнение
                ent
                assert $ == #1694
                disp #D694
                include "../ThreeD/ProjectRenderVertexGroup.asm"                ; (1) жёсткий порядок, продолжение подготовителя
                ent
                assert $ == #17A0
                disp #D7A0
                include "../ThreeD/ProjectRenderVertex.asm"
                ent
                assert $ == #1BBD
                disp #DBBD
                include "../ThreeD/RenderClippedRecords.asm"
                ent
                assert $ == #1D23
                disp #DD23
                include "../ThreeD/RenderInsideRecords.asm"
                ent
                assert $ == #1DD1
                disp #DDD1
                include "../ThreeD/CombineListedVertexCodes.asm"
                ent
                assert $ == #1DF0
                disp #DDF0
                include "../ThreeD/DrawLinearLine.asm"
                ent
                assert $ == #1EF0
                disp #DEF0
                include "../ThreeD/AbortProjectedVertexScan.asm"
                ent
                assert $ == #1EF3
                disp #DEF3
                include "../ThreeD/ClassifyProjectedVertices.asm"
                ent
                assert $ == #1FB6
                disp #DFB6
                include "../ThreeD/CheckFaceOrientation.asm"
                ent
                assert $ == #2009
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                incbin "../Resources/19_3DPART/Physical2009.bin"
                assert $ == #2010
                disp #E010
                include "../ThreeD/Data/LineMasks.asm"
                ent
                assert $ == #2020
                ; Unknown, сохранённые физические байты вне доказанных процедур и типизированных записей
                ; Физический суффикс выделенных секторов, неиспользуемость не установлена
                ; Документация [границы и сохранение суффиксов](../../Docs/AllocatedSectorSuffixes.md)
                incbin "../Resources/19_3DPART/SectorTail.bin"
                assert $ == #2100
