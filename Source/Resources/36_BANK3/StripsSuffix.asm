                module Bank3StripsSuffix
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #221E
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip14:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels14:       incbin "Strips/Strip14.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip15:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels15:       incbin "Strips/Strip15.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip16:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels16:       incbin "Strips/Strip16.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip17:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels17:       incbin "Strips/Strip17.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip18:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels18:       incbin "Strips/Strip18.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip19:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels19:       incbin "Strips/Strip19.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip20:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels20:       incbin "Strips/Strip20.bitmap"
                ; -----------------------------------------
                ; Экранная строка 97, высота 90, шесть байтов на строку
Strip21:        FScreenBitmapStrip {
                    #4980,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5A                                                         ; Height, число строк растра
                }
Pixels21:       incbin "Strips/Strip21.bitmap"
                ; -----------------------------------------
                ; Экранная строка 96, высота 91, шесть байтов на строку
Strip22:        FScreenBitmapStrip {
                    #4880,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5B                                                         ; Height, число строк растра
                }
Pixels22:       incbin "Strips/Strip22.bitmap"
                ; -----------------------------------------
                ; Экранная строка 96, высота 91, шесть байтов на строку
Strip23:        FScreenBitmapStrip {
                    #4880,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5B                                                         ; Height, число строк растра
                }
Pixels23:       incbin "Strips/Strip23.bitmap"
                ; -----------------------------------------
                ; Экранная строка 95, высота 92, шесть байтов на строку
Strip24:        FScreenBitmapStrip {
                    #4F60,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5C                                                         ; Height, число строк растра
                }
Pixels24:       incbin "Strips/Strip24.bitmap"
                ; -----------------------------------------
                ; Экранная строка 95, высота 92, шесть байтов на строку
Strip25:        FScreenBitmapStrip {
                    #4F60,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5C                                                         ; Height, число строк растра
                }
Pixels25:       incbin "Strips/Strip25.bitmap"
                ; -----------------------------------------
                ; Экранная строка 96, высота 91, шесть байтов на строку
Strip26:        FScreenBitmapStrip {
                    #4880,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5B                                                         ; Height, число строк растра
                }
Pixels26:       incbin "Strips/Strip26.bitmap"
                ; -----------------------------------------
                ; Экранная строка 96, высота 91, шесть байтов на строку
Strip27:        FScreenBitmapStrip {
                    #4880,                                                      ; ScreenAddress, исходное слово экранных координат
                    #5B                                                         ; Height, число строк растра
                }
Pixels27:       incbin "Strips/Strip27.bitmap"
                assert $ == #4000
                endmodule
