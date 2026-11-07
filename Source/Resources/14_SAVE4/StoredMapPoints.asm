                module Save4StoredMapPoints
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #00CF
Point00A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point01A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point02A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point03A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point04A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point05A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point06A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point07A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point08A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point09A:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
EndByteA:       db #80                                                          ; исходный байт границы списка, сохранён без нормализации
Point00B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point01B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point02B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point03B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point04B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point05B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point06B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point07B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point08B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
Point09B:       FStoredMapPoint {
                    #FFFF,                                                      ; FStoredMapPoint.FirstWord, значение дискового слота
                    #FFFF,                                                      ; FStoredMapPoint.SecondWord, значение дискового слота
                    #FF                                                         ; FStoredMapPoint.Variant, значение дискового слота
                }
EndByteB:       db #80                                                          ; исходный байт границы списка, сохранён без нормализации
                assert $ == #0135
                endmodule
