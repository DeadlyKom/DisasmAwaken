                module Save3SelectedMapKey
                ; Документация [сохраняемые поля игрока](../../../Docs/PlayerSavedFields.md)
                assert $ == #0009
Entry:          FSignatureInput {
                    #4B38,                                                      ; FSignatureInput.FirstWord, исходное значение
                    #4AF3,                                                      ; FSignatureInput.SecondWord, исходное значение
                    #00                                                         ; FSignatureInput.Variant, исходное значение
                }
                assert $ == #000E
                endmodule
