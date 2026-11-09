                module ActionClipTargetLowRow1
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF10
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetLowHead {
                    LOW(@Action.ClipRightToInside.Entry),                       ; SecondSides0, младший байт @Action.ClipRightToInside.Entry, индекс 10
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides1, младший байт @Action.ReturnClipCase.Entry, индекс 11
                    LOW(@Action.ClipRightToLeft.Entry),                         ; SecondSides2, младший байт @Action.ClipRightToLeft.Entry, индекс 12
                    #00,                                                        ; SecondSides3, индекс 13 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipRightToBottom.Entry),                       ; SecondSides4, младший байт @Action.ClipRightToBottom.Entry, индекс 14
                    LOW(@Action.ClipRightToBottomRight.Entry),                  ; SecondSides5, младший байт @Action.ClipRightToBottomRight.Entry, индекс 15
                    LOW(@Action.ClipRightToBottomLeft.Entry),                   ; SecondSides6, младший байт @Action.ClipRightToBottomLeft.Entry, индекс 16
                    #00,                                                        ; SecondSides7, индекс 17 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipRightToTop.Entry),                          ; SecondSides8, младший байт @Action.ClipRightToTop.Entry, индекс 18
                    LOW(@Action.ClipRightToTopRight.Entry),                     ; SecondSides9, младший байт @Action.ClipRightToTopRight.Entry, индекс 19
                    LOW(@Action.ClipRightToTopLeft.Entry)                       ; SecondSidesA, младший байт @Action.ClipRightToTopLeft.Entry, индекс 1A
                }
                assert $ == #CF1B
                endmodule
