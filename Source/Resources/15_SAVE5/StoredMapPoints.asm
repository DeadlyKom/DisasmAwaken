                module Save5StoredMapPoints
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #00CF
Point00A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point01A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point02A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point03A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point04A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point05A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point06A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point07A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point08A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point09A:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
EndByteA:       db #00                                                          ; исходный байт границы списка, сохранён без нормализации
Point00B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point01B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point02B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point03B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point04B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point05B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point06B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point07B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point08B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point09B:       FStoredMapPoint {
                    #0000,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #0000,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #00                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
EndByteB:       db #00                                                          ; исходный байт границы списка, сохранён без нормализации
                assert $ == #0135
                endmodule
