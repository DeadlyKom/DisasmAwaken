                module Save5InterfaceColors
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0187
InkBits:        FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
PaperRotate:    FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
HighRotate:     FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
                assert $ == #018D
                endmodule
