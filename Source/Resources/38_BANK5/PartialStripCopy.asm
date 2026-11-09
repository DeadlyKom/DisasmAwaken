                module Bank5PartialStripCopy
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #265C
                ; Неполная копия полосы BANK3, сохранены заголовок и 81 байтов растра
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip28:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, высота из исходного заголовка
                }
Pixels28:       incbin "Strips/Strip28.bitmap"
                assert $ == #26B0
                endmodule
