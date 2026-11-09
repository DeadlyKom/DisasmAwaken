                module ActionClipTargetLowRow2
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF20
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetLowHead {
                    LOW(@Action.ClipLeftToInside.Entry),                        ; SecondSides0, младший байт @Action.ClipLeftToInside.Entry, индекс 20
                    LOW(@Action.ClipLeftToRight.Entry),                         ; SecondSides1, младший байт @Action.ClipLeftToRight.Entry, индекс 21
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides2, младший байт @Action.ReturnClipCase.Entry, индекс 22
                    #00,                                                        ; SecondSides3, индекс 23 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipLeftToBottom.Entry),                        ; SecondSides4, младший байт @Action.ClipLeftToBottom.Entry, индекс 24
                    LOW(@Action.ClipLeftToBottomRight.Entry),                   ; SecondSides5, младший байт @Action.ClipLeftToBottomRight.Entry, индекс 25
                    LOW(@Action.ClipLeftToBottomLeft.Entry),                    ; SecondSides6, младший байт @Action.ClipLeftToBottomLeft.Entry, индекс 26
                    #00,                                                        ; SecondSides7, индекс 27 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipLeftToTop.Entry),                           ; SecondSides8, младший байт @Action.ClipLeftToTop.Entry, индекс 28
                    LOW(@Action.ClipLeftToTopRight.Entry),                      ; SecondSides9, младший байт @Action.ClipLeftToTopRight.Entry, индекс 29
                    LOW(@Action.ClipLeftToTopLeft.Entry)                        ; SecondSidesA, младший байт @Action.ClipLeftToTopLeft.Entry, индекс 2A
                }
                assert $ == #CF2B
                endmodule
