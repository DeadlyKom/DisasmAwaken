                module PreviewClipLeftHigh
                ; Документация [кэши произведений и разности](../../../Docs/PreviewClipProducts.md)
                assert $ == #C2FA
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewClipProductWord {
                    #0000                                                       ; Word, физическое слово разнесённого левого кэша, смысл младшего либо старшего задаётся именем экземпляра
                }
                assert $ == #C2FC
                endmodule
