                module Bank4PartialStripCopy
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #265C
                ; Неполная копия полосы BANK3, сохранены заголовок и 321 байтов растра
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip28:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, высота из исходного заголовка
                }
Pixels28:       incbin "Strips/Strip28.bitmap"
                assert $ == #27A0
                endmodule
