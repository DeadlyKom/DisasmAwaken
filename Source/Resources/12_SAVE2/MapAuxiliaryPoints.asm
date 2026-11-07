                module Save2MapAuxiliaryPoints
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0140
Key00:          FMapCoordinateKey {
                    #4B39,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0006                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key01:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key02:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key03:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key04:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key05:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key06:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key07:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key08:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
Key09:          FMapCoordinateKey {
                    #0000,                                                      ; FMapCoordinateKey.FirstWord, значение дискового слота
                    #0000                                                       ; FMapCoordinateKey.SecondWord, значение дискового слота
                }
                assert $ == #0168
                endmodule
