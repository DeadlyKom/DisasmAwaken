                module ThreeDClipTargetLowRow2
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF20
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetLowHead {
                    LOW(@ThreeD.ClipLeftToInside.Entry),                        ; SecondSides0, младший байт @ThreeD.ClipLeftToInside.Entry, индекс 20
                    LOW(@ThreeD.ClipLeftToRight.Entry),                         ; SecondSides1, младший байт @ThreeD.ClipLeftToRight.Entry, индекс 21
                    LOW(@ThreeD.ReturnClipCase.Entry),                          ; SecondSides2, младший байт @ThreeD.ReturnClipCase.Entry, индекс 22
                    #00,                                                        ; SecondSides3, индекс 23 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@ThreeD.ClipLeftToBottom.Entry),                        ; SecondSides4, младший байт @ThreeD.ClipLeftToBottom.Entry, индекс 24
                    LOW(@ThreeD.ClipLeftToBottomRight.Entry),                   ; SecondSides5, младший байт @ThreeD.ClipLeftToBottomRight.Entry, индекс 25
                    LOW(@ThreeD.ClipLeftToBottomLeft.Entry),                    ; SecondSides6, младший байт @ThreeD.ClipLeftToBottomLeft.Entry, индекс 26
                    #00,                                                        ; SecondSides7, индекс 27 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@ThreeD.ClipLeftToTop.Entry),                           ; SecondSides8, младший байт @ThreeD.ClipLeftToTop.Entry, индекс 28
                    LOW(@ThreeD.ClipLeftToTopRight.Entry),                      ; SecondSides9, младший байт @ThreeD.ClipLeftToTopRight.Entry, индекс 29
                    LOW(@ThreeD.ClipLeftToTopLeft.Entry)                        ; SecondSidesA, младший байт @ThreeD.ClipLeftToTopLeft.Entry, индекс 2A
                }
                assert $ == #CF2B
                endmodule
