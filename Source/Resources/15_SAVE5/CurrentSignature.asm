                module Save5CurrentSignature
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0004
Entry:          FSignatureInput {
                    #0000,                                                      ; FSignatureInput.FirstWord, значение дискового слота
                    #0000,                                                      ; FSignatureInput.SecondWord, значение дискового слота
                    #00                                                         ; FSignatureInput.Variant, значение дискового слота
                }
                assert $ == #0009
                endmodule
