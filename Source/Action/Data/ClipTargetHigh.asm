                module ActionClipTargetHigh
                ; Документация [физические таблицы заливки и диспетчера](../../../Docs/PolygonFillPhysicalData.md)
                assert $ == #D000
                ; -----------------------------------------
                ; исходная физическая запись FirstSides0
FirstSides0:    FClipTargetHighRow {
                    HIGH(@Action.AppendSecondClipPoint.Entry),                  ; SecondSides0, старший байт @Action.AppendSecondClipPoint.Entry, индекс 00
                    HIGH(@Action.ClipInsideToRight.Entry),                      ; SecondSides1, старший байт @Action.ClipInsideToRight.Entry, индекс 01
                    HIGH(@Action.ClipInsideToLeft.Entry),                       ; SecondSides2, старший байт @Action.ClipInsideToLeft.Entry, индекс 02
                    #00,                                                        ; SecondSides3, индекс 03 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipInsideToBottom.Entry),                     ; SecondSides4, старший байт @Action.ClipInsideToBottom.Entry, индекс 04
                    HIGH(@Action.ClipInsideToBottomRight.Entry),                ; SecondSides5, старший байт @Action.ClipInsideToBottomRight.Entry, индекс 05
                    HIGH(@Action.ClipInsideToBottomLeft.Entry),                 ; SecondSides6, старший байт @Action.ClipInsideToBottomLeft.Entry, индекс 06
                    #00,                                                        ; SecondSides7, индекс 07 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipInsideToTop.Entry),                        ; SecondSides8, старший байт @Action.ClipInsideToTop.Entry, индекс 08
                    HIGH(@Action.ClipInsideToTopRight.Entry),                   ; SecondSides9, старший байт @Action.ClipInsideToTopRight.Entry, индекс 09
                    HIGH(@Action.ClipInsideToTopLeft.Entry),                    ; SecondSidesA, старший байт @Action.ClipInsideToTopLeft.Entry, индекс 0A
                    #00,                                                        ; SecondSidesB, индекс 0B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 0C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 0D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 0E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 0F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetHighRow {
                    HIGH(@Action.ClipRightToInside.Entry),                      ; SecondSides0, старший байт @Action.ClipRightToInside.Entry, индекс 10
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides1, старший байт @Action.ReturnClipCase.Entry, индекс 11
                    HIGH(@Action.ClipRightToLeft.Entry),                        ; SecondSides2, старший байт @Action.ClipRightToLeft.Entry, индекс 12
                    #00,                                                        ; SecondSides3, индекс 13 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipRightToBottom.Entry),                      ; SecondSides4, старший байт @Action.ClipRightToBottom.Entry, индекс 14
                    HIGH(@Action.ClipRightToBottomRight.Entry),                 ; SecondSides5, старший байт @Action.ClipRightToBottomRight.Entry, индекс 15
                    HIGH(@Action.ClipRightToBottomLeft.Entry),                  ; SecondSides6, старший байт @Action.ClipRightToBottomLeft.Entry, индекс 16
                    #00,                                                        ; SecondSides7, индекс 17 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipRightToTop.Entry),                         ; SecondSides8, старший байт @Action.ClipRightToTop.Entry, индекс 18
                    HIGH(@Action.ClipRightToTopRight.Entry),                    ; SecondSides9, старший байт @Action.ClipRightToTopRight.Entry, индекс 19
                    HIGH(@Action.ClipRightToTopLeft.Entry),                     ; SecondSidesA, старший байт @Action.ClipRightToTopLeft.Entry, индекс 1A
                    #00,                                                        ; SecondSidesB, индекс 1B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 1C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 1D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 1E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 1F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetHighRow {
                    HIGH(@Action.ClipLeftToInside.Entry),                       ; SecondSides0, старший байт @Action.ClipLeftToInside.Entry, индекс 20
                    HIGH(@Action.ClipLeftToRight.Entry),                        ; SecondSides1, старший байт @Action.ClipLeftToRight.Entry, индекс 21
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides2, старший байт @Action.ReturnClipCase.Entry, индекс 22
                    #00,                                                        ; SecondSides3, индекс 23 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipLeftToBottom.Entry),                       ; SecondSides4, старший байт @Action.ClipLeftToBottom.Entry, индекс 24
                    HIGH(@Action.ClipLeftToBottomRight.Entry),                  ; SecondSides5, старший байт @Action.ClipLeftToBottomRight.Entry, индекс 25
                    HIGH(@Action.ClipLeftToBottomLeft.Entry),                   ; SecondSides6, старший байт @Action.ClipLeftToBottomLeft.Entry, индекс 26
                    #00,                                                        ; SecondSides7, индекс 27 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipLeftToTop.Entry),                          ; SecondSides8, старший байт @Action.ClipLeftToTop.Entry, индекс 28
                    HIGH(@Action.ClipLeftToTopRight.Entry),                     ; SecondSides9, старший байт @Action.ClipLeftToTopRight.Entry, индекс 29
                    HIGH(@Action.ClipLeftToTopLeft.Entry),                      ; SecondSidesA, старший байт @Action.ClipLeftToTopLeft.Entry, индекс 2A
                    #00,                                                        ; SecondSidesB, индекс 2B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 2C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 2D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 2E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 2F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides3
FirstSides3:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс 30 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс 31 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс 32 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс 33 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс 34 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс 35 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс 36 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс 37 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс 38 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс 39 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс 3A не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс 3B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 3C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 3D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 3E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 3F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides4
FirstSides4:    FClipTargetHighRow {
                    HIGH(@Action.ClipBottomToInside.Entry),                     ; SecondSides0, старший байт @Action.ClipBottomToInside.Entry, индекс 40
                    HIGH(@Action.ClipBottomToRight.Entry),                      ; SecondSides1, старший байт @Action.ClipBottomToRight.Entry, индекс 41
                    HIGH(@Action.ClipBottomToLeft.Entry),                       ; SecondSides2, старший байт @Action.ClipBottomToLeft.Entry, индекс 42
                    #00,                                                        ; SecondSides3, индекс 43 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides4, старший байт @Action.ReturnClipCase.Entry, индекс 44
                    HIGH(@Action.ClipBottomToBottomRight.Entry),                ; SecondSides5, старший байт @Action.ClipBottomToBottomRight.Entry, индекс 45
                    HIGH(@Action.ClipBottomToBottomLeft.Entry),                 ; SecondSides6, старший байт @Action.ClipBottomToBottomLeft.Entry, индекс 46
                    #00,                                                        ; SecondSides7, индекс 47 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipBottomToTop.Entry),                        ; SecondSides8, старший байт @Action.ClipBottomToTop.Entry, индекс 48
                    HIGH(@Action.ClipBottomToTopRight.Entry),                   ; SecondSides9, старший байт @Action.ClipBottomToTopRight.Entry, индекс 49
                    HIGH(@Action.ClipBottomToTopLeft.Entry),                    ; SecondSidesA, старший байт @Action.ClipBottomToTopLeft.Entry, индекс 4A
                    #00,                                                        ; SecondSidesB, индекс 4B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 4C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 4D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 4E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 4F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides5
FirstSides5:    FClipTargetHighRow {
                    HIGH(@Action.ClipBottomRightToInside.Entry),                ; SecondSides0, старший байт @Action.ClipBottomRightToInside.Entry, индекс 50
                    HIGH(@Action.ClipBottomRightToRight.Entry),                 ; SecondSides1, старший байт @Action.ClipBottomRightToRight.Entry, индекс 51
                    HIGH(@Action.ClipBottomRightToLeft.Entry),                  ; SecondSides2, старший байт @Action.ClipBottomRightToLeft.Entry, индекс 52
                    #00,                                                        ; SecondSides3, индекс 53 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipBottomRightToBottom.Entry),                ; SecondSides4, старший байт @Action.ClipBottomRightToBottom.Entry, индекс 54
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides5, старший байт @Action.ReturnClipCase.Entry, индекс 55
                    HIGH(@Action.ClipBottomRightToBottomLeft.Entry),            ; SecondSides6, старший байт @Action.ClipBottomRightToBottomLeft.Entry, индекс 56
                    #00,                                                        ; SecondSides7, индекс 57 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipBottomRightToTop.Entry),                   ; SecondSides8, старший байт @Action.ClipBottomRightToTop.Entry, индекс 58
                    HIGH(@Action.ExitClipContour.Entry),                        ; SecondSides9, старший байт @Action.ExitClipContour.Entry, индекс 59
                    HIGH(@Action.ClipBottomRightToTopLeft.Entry),               ; SecondSidesA, старший байт @Action.ClipBottomRightToTopLeft.Entry, индекс 5A
                    #00,                                                        ; SecondSidesB, индекс 5B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 5C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 5D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 5E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 5F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides6
FirstSides6:    FClipTargetHighRow {
                    HIGH(@Action.ClipBottomLeftToInside.Entry),                 ; SecondSides0, старший байт @Action.ClipBottomLeftToInside.Entry, индекс 60
                    HIGH(@Action.ClipBottomLeftToRight.Entry),                  ; SecondSides1, старший байт @Action.ClipBottomLeftToRight.Entry, индекс 61
                    HIGH(@Action.ClipBottomLeftToLeft.Entry),                   ; SecondSides2, старший байт @Action.ClipBottomLeftToLeft.Entry, индекс 62
                    #00,                                                        ; SecondSides3, индекс 63 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipBottomLeftToBottom.Entry),                 ; SecondSides4, старший байт @Action.ClipBottomLeftToBottom.Entry, индекс 64
                    HIGH(@Action.ExitClipContour.Entry),                        ; SecondSides5, старший байт @Action.ExitClipContour.Entry, индекс 65
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides6, старший байт @Action.ReturnClipCase.Entry, индекс 66
                    #00,                                                        ; SecondSides7, индекс 67 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipBottomLeftToTop.Entry),                    ; SecondSides8, старший байт @Action.ClipBottomLeftToTop.Entry, индекс 68
                    HIGH(@Action.ClipBottomLeftToTopRight.Entry),               ; SecondSides9, старший байт @Action.ClipBottomLeftToTopRight.Entry, индекс 69
                    HIGH(@Action.ClipBottomLeftToTopLeft.Entry),                ; SecondSidesA, старший байт @Action.ClipBottomLeftToTopLeft.Entry, индекс 6A
                    #00,                                                        ; SecondSidesB, индекс 6B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 6C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 6D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 6E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 6F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides7
FirstSides7:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс 70 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс 71 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс 72 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс 73 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс 74 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс 75 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс 76 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс 77 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс 78 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс 79 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс 7A не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс 7B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 7C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 7D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 7E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 7F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides8
FirstSides8:    FClipTargetHighRow {
                    HIGH(@Action.ClipTopToInside.Entry),                        ; SecondSides0, старший байт @Action.ClipTopToInside.Entry, индекс 80
                    HIGH(@Action.ClipTopToRight.Entry),                         ; SecondSides1, старший байт @Action.ClipTopToRight.Entry, индекс 81
                    HIGH(@Action.ClipTopToLeft.Entry),                          ; SecondSides2, старший байт @Action.ClipTopToLeft.Entry, индекс 82
                    #00,                                                        ; SecondSides3, индекс 83 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipTopToBottom.Entry),                        ; SecondSides4, старший байт @Action.ClipTopToBottom.Entry, индекс 84
                    HIGH(@Action.ClipTopToBottomRight.Entry),                   ; SecondSides5, старший байт @Action.ClipTopToBottomRight.Entry, индекс 85
                    HIGH(@Action.ClipTopToBottomLeft.Entry),                    ; SecondSides6, старший байт @Action.ClipTopToBottomLeft.Entry, индекс 86
                    #00,                                                        ; SecondSides7, индекс 87 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides8, старший байт @Action.ReturnClipCase.Entry, индекс 88
                    HIGH(@Action.ClipTopToTopRight.Entry),                      ; SecondSides9, старший байт @Action.ClipTopToTopRight.Entry, индекс 89
                    HIGH(@Action.ClipTopToTopLeft.Entry),                       ; SecondSidesA, старший байт @Action.ClipTopToTopLeft.Entry, индекс 8A
                    #00,                                                        ; SecondSidesB, индекс 8B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 8C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 8D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 8E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 8F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides9
FirstSides9:    FClipTargetHighRow {
                    HIGH(@Action.ClipTopRightToInside.Entry),                   ; SecondSides0, старший байт @Action.ClipTopRightToInside.Entry, индекс 90
                    HIGH(@Action.ClipTopRightToRight.Entry),                    ; SecondSides1, старший байт @Action.ClipTopRightToRight.Entry, индекс 91
                    HIGH(@Action.ClipTopRightToLeft.Entry),                     ; SecondSides2, старший байт @Action.ClipTopRightToLeft.Entry, индекс 92
                    #00,                                                        ; SecondSides3, индекс 93 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipTopRightToBottom.Entry),                   ; SecondSides4, старший байт @Action.ClipTopRightToBottom.Entry, индекс 94
                    HIGH(@Action.ClipTopRightToBottomRight.Entry),              ; SecondSides5, старший байт @Action.ClipTopRightToBottomRight.Entry, индекс 95
                    HIGH(@Action.ClipTopRightToBottomLeft.Entry),               ; SecondSides6, старший байт @Action.ClipTopRightToBottomLeft.Entry, индекс 96
                    #00,                                                        ; SecondSides7, индекс 97 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipTopRightToTop.Entry),                      ; SecondSides8, старший байт @Action.ClipTopRightToTop.Entry, индекс 98
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSides9, старший байт @Action.ReturnClipCase.Entry, индекс 99
                    HIGH(@Action.ExitClipContour.Entry),                        ; SecondSidesA, старший байт @Action.ExitClipContour.Entry, индекс 9A
                    #00,                                                        ; SecondSidesB, индекс 9B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 9C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 9D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 9E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 9F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesA
FirstSidesA:    FClipTargetHighRow {
                    HIGH(@Action.ClipTopLeftToInside.Entry),                    ; SecondSides0, старший байт @Action.ClipTopLeftToInside.Entry, индекс A0
                    HIGH(@Action.ClipTopLeftToRight.Entry),                     ; SecondSides1, старший байт @Action.ClipTopLeftToRight.Entry, индекс A1
                    HIGH(@Action.ClipTopLeftToLeft.Entry),                      ; SecondSides2, старший байт @Action.ClipTopLeftToLeft.Entry, индекс A2
                    #00,                                                        ; SecondSides3, индекс A3 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipTopLeftToBottom.Entry),                    ; SecondSides4, старший байт @Action.ClipTopLeftToBottom.Entry, индекс A4
                    HIGH(@Action.ClipTopLeftToBottomRight.Entry),               ; SecondSides5, старший байт @Action.ClipTopLeftToBottomRight.Entry, индекс A5
                    HIGH(@Action.ExitClipContour.Entry),                        ; SecondSides6, старший байт @Action.ExitClipContour.Entry, индекс A6
                    #00,                                                        ; SecondSides7, индекс A7 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@Action.ClipTopLeftToTop.Entry),                       ; SecondSides8, старший байт @Action.ClipTopLeftToTop.Entry, индекс A8
                    HIGH(@Action.ClipTopLeftToTopRight.Entry),                  ; SecondSides9, старший байт @Action.ClipTopLeftToTopRight.Entry, индекс A9
                    HIGH(@Action.ReturnClipCase.Entry),                         ; SecondSidesA, старший байт @Action.ReturnClipCase.Entry, индекс AA
                    #00,                                                        ; SecondSidesB, индекс AB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс AC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс AD не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс AE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс AF не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesB
FirstSidesB:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс B0 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс B1 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс B2 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс B3 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс B4 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс B5 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс B6 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс B7 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс B8 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс B9 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс BA не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс BB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс BC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс BD не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс BE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс BF не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesC
FirstSidesC:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс C0 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс C1 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс C2 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс C3 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс C4 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс C5 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс C6 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс C7 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс C8 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс C9 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс CA не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс CB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс CC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс CD не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс CE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс CF не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesD
FirstSidesD:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс D0 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс D1 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс D2 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс D3 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс D4 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс D5 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс D6 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс D7 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс D8 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс D9 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс DA не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс DB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс DC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс DD не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс DE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс DF не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesE
FirstSidesE:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс E0 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс E1 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс E2 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс E3 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс E4 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс E5 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс E6 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс E7 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс E8 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс E9 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс EA не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс EB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс EC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс ED не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс EE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс EF не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesF
FirstSidesF:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, индекс F0 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс F1 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс F2 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс F3 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс F4 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс F5 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс F6 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс F7 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс F8 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс F9 не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс FA не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс FB не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс FC не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс FD не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс FE не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс FF не получается из 81 нормальной пары, исходный байт сохранён
                }
                assert $ == #D100
                endmodule
