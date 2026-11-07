                module Save0CurrentSignature
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0004
Entry:          FSignatureInput {
                    #4B38,                                                      ; FSignatureInput.FirstWord, значение дискового слота
                    #4AF3,                                                      ; FSignatureInput.SecondWord, значение дискового слота
                    #00                                                         ; FSignatureInput.Variant, значение дискового слота
                }
                assert $ == #0009
                endmodule
