                module PreviewClipRightProduct
                ; Документация [кэши произведений и разности](../../../Docs/PreviewClipProducts.md)
                assert $ == #C2FC
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FClipProduct {
                    #0000,                                                      ; LowWord, младшее слово исходного результата умножения
                    #0000                                                       ; HighWord, старшее слово того же 32-битного результата
                }
                assert $ == #C300
                endmodule
