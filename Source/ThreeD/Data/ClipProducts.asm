                module ThreeDClipProductsData
                ; Документация [произведения пересечений](../../../Docs/ThreeDOverlayMirror.md)
                assert $ == #CF2B
RightProduct:   FClipProduct {
                    #0000,                                                      ; LowWord, исходное младшее слово числителя
                    #0000                                                       ; HighWord, исходное старшее слово числителя
                }
LeftProduct:    FClipProduct {
                    #0000,                                                      ; LowWord, исходное младшее слово числителя
                    #0000                                                       ; HighWord, исходное старшее слово числителя
                }
BottomProduct:  FClipProduct {
                    #0000,                                                      ; LowWord, исходное младшее слово числителя
                    #0000                                                       ; HighWord, исходное старшее слово числителя
                }
TopProduct:     FClipProduct {
                    #0000,                                                      ; LowWord, исходное младшее слово числителя
                    #0000                                                       ; HighWord, исходное старшее слово числителя
                }
                assert $ == #CF3B
                endmodule
