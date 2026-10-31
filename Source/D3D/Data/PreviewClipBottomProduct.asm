                module PreviewClipBottomProduct
                ; Документация [кэши произведений и разности](../../../Docs/PreviewClipProducts.md)
                assert $ == #C2EA
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FClipProduct {
                    #0000,                                                      ; LowWord, младшее слово исходного результата умножения
                    #0000                                                       ; HighWord, старшее слово того же 32-битного результата
                }
                assert $ == #C2EE
                endmodule
