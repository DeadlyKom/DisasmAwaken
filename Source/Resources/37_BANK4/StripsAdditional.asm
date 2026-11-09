                module Bank4StripsAdditional
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #221E
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip26:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels26:       incbin "Strips/Strip26.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip27:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels27:       incbin "Strips/Strip27.bitmap"
                assert $ == #265C
                endmodule
