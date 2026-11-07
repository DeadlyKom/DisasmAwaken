                module Save3ControlOptions
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #018D
Unknown00:      FSettingWord {
                    #81,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown01:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown02:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown03:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown04:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown05:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown06:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown07:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown08:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown09:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown10:      FSettingWord {
                    #DF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown11:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown12:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown13:      FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown14:      FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown15:      FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown16:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown17:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown18:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown19:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown20:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown21:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown22:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown23:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown24:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown25:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown26:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown27:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown28:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown29:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown30:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown31:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown32:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown33:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #02                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown34:      FSettingWord {
                    #DF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown35:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown36:      FSettingWord {
                    #FE,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown37:      FSettingWord {
                    #F7,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown38:      FSettingWord {
                    #BF,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #08                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown39:      FSettingWord {
                    #FB,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #01                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown40:      FSettingWord {
                    #FD,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #04                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown41:      FSettingWord {
                    #7F,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #10                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
Unknown42:      FSettingWord {
                    #00,                                                        ; FSettingWord.ValueOrRow, значение дискового слота
                    #00                                                         ; FSettingWord.KeyMask, значение дискового слота
                }
                assert $ == #01E3
                endmodule
