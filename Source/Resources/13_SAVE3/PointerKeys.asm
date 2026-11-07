                module Save3PointerKeys
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #017B
Up:             FKeyBinding {
                    #FB,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #01                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Down:           FKeyBinding {
                    #FD,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #01                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Left:           FKeyBinding {
                    #DF,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #02                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Right:          FKeyBinding {
                    #DF,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #01                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Action2:        FKeyBinding {
                    #7F,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #01                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Action1:        FKeyBinding {
                    #7F,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #04                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
                assert $ == #0187
                endmodule
