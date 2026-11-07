                module Save5SelectedMapKey
                ; Документация [сохраняемые поля игрока](../../../Docs/PlayerSavedFields.md)
                assert $ == #0009
Entry:          FSignatureInput {
                    #0000,                                                      ; FSignatureInput.FirstWord, исходное значение
                    #0000,                                                      ; FSignatureInput.SecondWord, исходное значение
                    #00                                                         ; FSignatureInput.Variant, исходное значение
                }
                assert $ == #000E
                endmodule
