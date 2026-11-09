                module ThreeDClipTargetLowRow1
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF10
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetLowHead {
                    LOW(@ThreeD.ClipRightToInside.Entry),                       ; SecondSides0, младший байт @ThreeD.ClipRightToInside.Entry, индекс 10
                    LOW(@ThreeD.ReturnClipCase.Entry),                          ; SecondSides1, младший байт @ThreeD.ReturnClipCase.Entry, индекс 11
                    LOW(@ThreeD.ClipRightToLeft.Entry),                         ; SecondSides2, младший байт @ThreeD.ClipRightToLeft.Entry, индекс 12
                    #00,                                                        ; SecondSides3, индекс 13 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@ThreeD.ClipRightToBottom.Entry),                       ; SecondSides4, младший байт @ThreeD.ClipRightToBottom.Entry, индекс 14
                    LOW(@ThreeD.ClipRightToBottomRight.Entry),                  ; SecondSides5, младший байт @ThreeD.ClipRightToBottomRight.Entry, индекс 15
                    LOW(@ThreeD.ClipRightToBottomLeft.Entry),                   ; SecondSides6, младший байт @ThreeD.ClipRightToBottomLeft.Entry, индекс 16
                    #00,                                                        ; SecondSides7, индекс 17 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@ThreeD.ClipRightToTop.Entry),                          ; SecondSides8, младший байт @ThreeD.ClipRightToTop.Entry, индекс 18
                    LOW(@ThreeD.ClipRightToTopRight.Entry),                     ; SecondSides9, младший байт @ThreeD.ClipRightToTopRight.Entry, индекс 19
                    LOW(@ThreeD.ClipRightToTopLeft.Entry)                       ; SecondSidesA, младший байт @ThreeD.ClipRightToTopLeft.Entry, индекс 1A
                }
                assert $ == #CF1B
                endmodule
