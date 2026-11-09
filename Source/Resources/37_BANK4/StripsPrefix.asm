                module Bank4StripsPrefix
                ; Метки являются смещениями файла BANK, номер аппаратного банка не назначается
                ; Документация [заголовки и растры BANK](../../../Docs/BankScreenStrips.md)
                assert $ == #0000
                ; -----------------------------------------
                ; Экранная строка 106, высота 81, шесть байтов на строку
Strip00:        FScreenBitmapStrip {
                    #4AA0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #51                                                         ; Height, число строк растра
                }
Pixels00:       incbin "Strips/Strip00.bitmap"
                ; -----------------------------------------
                ; Экранная строка 106, высота 81, шесть байтов на строку
Strip01:        FScreenBitmapStrip {
                    #4AA0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #51                                                         ; Height, число строк растра
                }
Pixels01:       incbin "Strips/Strip01.bitmap"
                ; -----------------------------------------
                ; Экранная строка 105, высота 82, шесть байтов на строку
Strip02:        FScreenBitmapStrip {
                    #49A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #52                                                         ; Height, число строк растра
                }
Pixels02:       incbin "Strips/Strip02.bitmap"
                ; -----------------------------------------
                ; Экранная строка 105, высота 82, шесть байтов на строку
Strip03:        FScreenBitmapStrip {
                    #49A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #52                                                         ; Height, число строк растра
                }
Pixels03:       incbin "Strips/Strip03.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip04:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels04:       incbin "Strips/Strip04.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip05:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels05:       incbin "Strips/Strip05.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip06:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels06:       incbin "Strips/Strip06.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip07:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels07:       incbin "Strips/Strip07.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip08:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels08:       incbin "Strips/Strip08.bitmap"
                ; -----------------------------------------
                ; Экранная строка 103, высота 84, шесть байтов на строку
Strip09:        FScreenBitmapStrip {
                    #4F80,                                                      ; ScreenAddress, исходное слово экранных координат
                    #54                                                         ; Height, число строк растра
                }
Pixels09:       incbin "Strips/Strip09.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip10:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels10:       incbin "Strips/Strip10.bitmap"
                ; -----------------------------------------
                ; Экранная строка 104, высота 83, шесть байтов на строку
Strip11:        FScreenBitmapStrip {
                    #48A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #53                                                         ; Height, число строк растра
                }
Pixels11:       incbin "Strips/Strip11.bitmap"
                ; -----------------------------------------
                ; Экранная строка 105, высота 82, шесть байтов на строку
Strip12:        FScreenBitmapStrip {
                    #49A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #52                                                         ; Height, число строк растра
                }
Pixels12:       incbin "Strips/Strip12.bitmap"
                ; -----------------------------------------
                ; Экранная строка 105, высота 82, шесть байтов на строку
Strip13:        FScreenBitmapStrip {
                    #49A0,                                                      ; ScreenAddress, исходное слово экранных координат
                    #52                                                         ; Height, число строк растра
                }
Pixels13:       incbin "Strips/Strip13.bitmap"
                assert $ == #1B4E
                endmodule
