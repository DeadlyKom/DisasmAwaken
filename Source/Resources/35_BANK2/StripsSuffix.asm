                module Bank2StripsSuffix
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #242E
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip14:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels14:       incbin "Strips/Strip14.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip15:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels15:       incbin "Strips/Strip15.bitmap"
                ; -----------------------------------------
                ; Экранная строка 102, высота 85, шесть байтов на строку
Strip16:        FScreenBitmapStrip {
                    #4E80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #55                                                         ; Height, число строк растра
                }
Pixels16:       incbin "Strips/Strip16.bitmap"
                ; -----------------------------------------
                ; Экранная строка 102, высота 85, шесть байтов на строку
Strip17:        FScreenBitmapStrip {
                    #4E80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #55                                                         ; Height, число строк растра
                }
Pixels17:       incbin "Strips/Strip17.bitmap"
                ; -----------------------------------------
                ; Экранная строка 101, высота 86, шесть байтов на строку
Strip18:        FScreenBitmapStrip {
                    #4D80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #56                                                         ; Height, число строк растра
                }
Pixels18:       incbin "Strips/Strip18.bitmap"
                ; -----------------------------------------
                ; Экранная строка 101, высота 86, шесть байтов на строку
Strip19:        FScreenBitmapStrip {
                    #4D80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #56                                                         ; Height, число строк растра
                }
Pixels19:       incbin "Strips/Strip19.bitmap"
                ; -----------------------------------------
                ; Экранная строка 102, высота 85, шесть байтов на строку
Strip20:        FScreenBitmapStrip {
                    #4E80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #55                                                         ; Height, число строк растра
                }
Pixels20:       incbin "Strips/Strip20.bitmap"
                ; -----------------------------------------
                ; Экранная строка 102, высота 85, шесть байтов на строку
Strip21:        FScreenBitmapStrip {
                    #4E80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #55                                                         ; Height, число строк растра
                }
Pixels21:       incbin "Strips/Strip21.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip22:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels22:       incbin "Strips/Strip22.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip23:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels23:       incbin "Strips/Strip23.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip24:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels24:       incbin "Strips/Strip24.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip25:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels25:       incbin "Strips/Strip25.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip26:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels26:       incbin "Strips/Strip26.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip27:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels27:       incbin "Strips/Strip27.bitmap"
                assert $ == #4000
                endmodule
