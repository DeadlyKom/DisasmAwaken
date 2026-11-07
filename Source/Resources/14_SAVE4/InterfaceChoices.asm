                module Save4InterfaceChoices
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0173
MouseOption:    FSettingWord {
                    #81,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
JoyOption:      FSettingWord {
                    #80,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
MusicMode:      FSettingWord {
                    #81,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
FillMode:       FSettingWord {
                    #80,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
                assert $ == #017B
                endmodule
