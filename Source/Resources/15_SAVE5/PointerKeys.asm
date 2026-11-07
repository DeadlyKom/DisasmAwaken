                module Save5PointerKeys
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #017B
Up:             FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Down:           FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Left:           FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Right:          FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Action2:        FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
Action1:        FKeyBinding {
                    #00,                                                        ; FKeyBinding.RowMask, значение дискового слота
                    #00                                                         ; FKeyBinding.KeyMask, значение дискового слота
                }
                assert $ == #0187
                endmodule
