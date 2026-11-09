                module ThreeDClipTargetHigh
                ; Документация [физические таблицы заливки и диспетчера](../../../Docs/PolygonFillPhysicalData.md)
                assert $ == #D000
                ; -----------------------------------------
                ; исходная физическая запись FirstSides0
FirstSides0:    FClipTargetHighRow {
                    HIGH(@ThreeD.AppendSecondClipPoint.Entry),                  ; SecondSides0, старший байт @ThreeD.AppendSecondClipPoint.Entry, индекс 00
                    HIGH(@ThreeD.ClipInsideToRight.Entry),                      ; SecondSides1, старший байт @ThreeD.ClipInsideToRight.Entry, индекс 01
                    HIGH(@ThreeD.ClipInsideToLeft.Entry),                       ; SecondSides2, старший байт @ThreeD.ClipInsideToLeft.Entry, индекс 02
                    #00,                                                        ; SecondSides3, индекс 03 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipInsideToBottom.Entry),                     ; SecondSides4, старший байт @ThreeD.ClipInsideToBottom.Entry, индекс 04
                    HIGH(@ThreeD.ClipInsideToBottomRight.Entry),                ; SecondSides5, старший байт @ThreeD.ClipInsideToBottomRight.Entry, индекс 05
                    HIGH(@ThreeD.ClipInsideToBottomLeft.Entry),                 ; SecondSides6, старший байт @ThreeD.ClipInsideToBottomLeft.Entry, индекс 06
                    #00,                                                        ; SecondSides7, индекс 07 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipInsideToTop.Entry),                        ; SecondSides8, старший байт @ThreeD.ClipInsideToTop.Entry, индекс 08
                    HIGH(@ThreeD.ClipInsideToTopRight.Entry),                   ; SecondSides9, старший байт @ThreeD.ClipInsideToTopRight.Entry, индекс 09
                    HIGH(@ThreeD.ClipInsideToTopLeft.Entry),                    ; SecondSidesA, старший байт @ThreeD.ClipInsideToTopLeft.Entry, индекс 0A
                    #00,                                                        ; SecondSidesB, индекс 0B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 0C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 0D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 0E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 0F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipRightToInside.Entry),                      ; SecondSides0, старший байт @ThreeD.ClipRightToInside.Entry, индекс 10
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides1, старший байт @ThreeD.ReturnClipCase.Entry, индекс 11
                    HIGH(@ThreeD.ClipRightToLeft.Entry),                        ; SecondSides2, старший байт @ThreeD.ClipRightToLeft.Entry, индекс 12
                    #00,                                                        ; SecondSides3, индекс 13 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipRightToBottom.Entry),                      ; SecondSides4, старший байт @ThreeD.ClipRightToBottom.Entry, индекс 14
                    HIGH(@ThreeD.ClipRightToBottomRight.Entry),                 ; SecondSides5, старший байт @ThreeD.ClipRightToBottomRight.Entry, индекс 15
                    HIGH(@ThreeD.ClipRightToBottomLeft.Entry),                  ; SecondSides6, старший байт @ThreeD.ClipRightToBottomLeft.Entry, индекс 16
                    #00,                                                        ; SecondSides7, индекс 17 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipRightToTop.Entry),                         ; SecondSides8, старший байт @ThreeD.ClipRightToTop.Entry, индекс 18
                    HIGH(@ThreeD.ClipRightToTopRight.Entry),                    ; SecondSides9, старший байт @ThreeD.ClipRightToTopRight.Entry, индекс 19
                    HIGH(@ThreeD.ClipRightToTopLeft.Entry),                     ; SecondSidesA, старший байт @ThreeD.ClipRightToTopLeft.Entry, индекс 1A
                    #00,                                                        ; SecondSidesB, индекс 1B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 1C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 1D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 1E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 1F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipLeftToInside.Entry),                       ; SecondSides0, старший байт @ThreeD.ClipLeftToInside.Entry, индекс 20
                    HIGH(@ThreeD.ClipLeftToRight.Entry),                        ; SecondSides1, старший байт @ThreeD.ClipLeftToRight.Entry, индекс 21
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides2, старший байт @ThreeD.ReturnClipCase.Entry, индекс 22
                    #00,                                                        ; SecondSides3, индекс 23 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipLeftToBottom.Entry),                       ; SecondSides4, старший байт @ThreeD.ClipLeftToBottom.Entry, индекс 24
                    HIGH(@ThreeD.ClipLeftToBottomRight.Entry),                  ; SecondSides5, старший байт @ThreeD.ClipLeftToBottomRight.Entry, индекс 25
                    HIGH(@ThreeD.ClipLeftToBottomLeft.Entry),                   ; SecondSides6, старший байт @ThreeD.ClipLeftToBottomLeft.Entry, индекс 26
                    #00,                                                        ; SecondSides7, индекс 27 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipLeftToTop.Entry),                          ; SecondSides8, старший байт @ThreeD.ClipLeftToTop.Entry, индекс 28
                    HIGH(@ThreeD.ClipLeftToTopRight.Entry),                     ; SecondSides9, старший байт @ThreeD.ClipLeftToTopRight.Entry, индекс 29
                    HIGH(@ThreeD.ClipLeftToTopLeft.Entry),                      ; SecondSidesA, старший байт @ThreeD.ClipLeftToTopLeft.Entry, индекс 2A
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
                    HIGH(@ThreeD.ClipBottomToInside.Entry),                     ; SecondSides0, старший байт @ThreeD.ClipBottomToInside.Entry, индекс 40
                    HIGH(@ThreeD.ClipBottomToRight.Entry),                      ; SecondSides1, старший байт @ThreeD.ClipBottomToRight.Entry, индекс 41
                    HIGH(@ThreeD.ClipBottomToLeft.Entry),                       ; SecondSides2, старший байт @ThreeD.ClipBottomToLeft.Entry, индекс 42
                    #00,                                                        ; SecondSides3, индекс 43 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides4, старший байт @ThreeD.ReturnClipCase.Entry, индекс 44
                    HIGH(@ThreeD.ClipBottomToBottomRight.Entry),                ; SecondSides5, старший байт @ThreeD.ClipBottomToBottomRight.Entry, индекс 45
                    HIGH(@ThreeD.ClipBottomToBottomLeft.Entry),                 ; SecondSides6, старший байт @ThreeD.ClipBottomToBottomLeft.Entry, индекс 46
                    #00,                                                        ; SecondSides7, индекс 47 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipBottomToTop.Entry),                        ; SecondSides8, старший байт @ThreeD.ClipBottomToTop.Entry, индекс 48
                    HIGH(@ThreeD.ClipBottomToTopRight.Entry),                   ; SecondSides9, старший байт @ThreeD.ClipBottomToTopRight.Entry, индекс 49
                    HIGH(@ThreeD.ClipBottomToTopLeft.Entry),                    ; SecondSidesA, старший байт @ThreeD.ClipBottomToTopLeft.Entry, индекс 4A
                    #00,                                                        ; SecondSidesB, индекс 4B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 4C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 4D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 4E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 4F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides5
FirstSides5:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipBottomRightToInside.Entry),                ; SecondSides0, старший байт @ThreeD.ClipBottomRightToInside.Entry, индекс 50
                    HIGH(@ThreeD.ClipBottomRightToRight.Entry),                 ; SecondSides1, старший байт @ThreeD.ClipBottomRightToRight.Entry, индекс 51
                    HIGH(@ThreeD.ClipBottomRightToLeft.Entry),                  ; SecondSides2, старший байт @ThreeD.ClipBottomRightToLeft.Entry, индекс 52
                    #00,                                                        ; SecondSides3, индекс 53 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipBottomRightToBottom.Entry),                ; SecondSides4, старший байт @ThreeD.ClipBottomRightToBottom.Entry, индекс 54
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides5, старший байт @ThreeD.ReturnClipCase.Entry, индекс 55
                    HIGH(@ThreeD.ClipBottomRightToBottomLeft.Entry),            ; SecondSides6, старший байт @ThreeD.ClipBottomRightToBottomLeft.Entry, индекс 56
                    #00,                                                        ; SecondSides7, индекс 57 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipBottomRightToTop.Entry),                   ; SecondSides8, старший байт @ThreeD.ClipBottomRightToTop.Entry, индекс 58
                    HIGH(@ThreeD.ExitClipContour.Entry),                        ; SecondSides9, старший байт @ThreeD.ExitClipContour.Entry, индекс 59
                    HIGH(@ThreeD.ClipBottomRightToTopLeft.Entry),               ; SecondSidesA, старший байт @ThreeD.ClipBottomRightToTopLeft.Entry, индекс 5A
                    #00,                                                        ; SecondSidesB, индекс 5B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 5C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 5D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 5E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 5F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides6
FirstSides6:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipBottomLeftToInside.Entry),                 ; SecondSides0, старший байт @ThreeD.ClipBottomLeftToInside.Entry, индекс 60
                    HIGH(@ThreeD.ClipBottomLeftToRight.Entry),                  ; SecondSides1, старший байт @ThreeD.ClipBottomLeftToRight.Entry, индекс 61
                    HIGH(@ThreeD.ClipBottomLeftToLeft.Entry),                   ; SecondSides2, старший байт @ThreeD.ClipBottomLeftToLeft.Entry, индекс 62
                    #00,                                                        ; SecondSides3, индекс 63 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipBottomLeftToBottom.Entry),                 ; SecondSides4, старший байт @ThreeD.ClipBottomLeftToBottom.Entry, индекс 64
                    HIGH(@ThreeD.ExitClipContour.Entry),                        ; SecondSides5, старший байт @ThreeD.ExitClipContour.Entry, индекс 65
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides6, старший байт @ThreeD.ReturnClipCase.Entry, индекс 66
                    #00,                                                        ; SecondSides7, индекс 67 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipBottomLeftToTop.Entry),                    ; SecondSides8, старший байт @ThreeD.ClipBottomLeftToTop.Entry, индекс 68
                    HIGH(@ThreeD.ClipBottomLeftToTopRight.Entry),               ; SecondSides9, старший байт @ThreeD.ClipBottomLeftToTopRight.Entry, индекс 69
                    HIGH(@ThreeD.ClipBottomLeftToTopLeft.Entry),                ; SecondSidesA, старший байт @ThreeD.ClipBottomLeftToTopLeft.Entry, индекс 6A
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
                    HIGH(@ThreeD.ClipTopToInside.Entry),                        ; SecondSides0, старший байт @ThreeD.ClipTopToInside.Entry, индекс 80
                    HIGH(@ThreeD.ClipTopToRight.Entry),                         ; SecondSides1, старший байт @ThreeD.ClipTopToRight.Entry, индекс 81
                    HIGH(@ThreeD.ClipTopToLeft.Entry),                          ; SecondSides2, старший байт @ThreeD.ClipTopToLeft.Entry, индекс 82
                    #00,                                                        ; SecondSides3, индекс 83 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipTopToBottom.Entry),                        ; SecondSides4, старший байт @ThreeD.ClipTopToBottom.Entry, индекс 84
                    HIGH(@ThreeD.ClipTopToBottomRight.Entry),                   ; SecondSides5, старший байт @ThreeD.ClipTopToBottomRight.Entry, индекс 85
                    HIGH(@ThreeD.ClipTopToBottomLeft.Entry),                    ; SecondSides6, старший байт @ThreeD.ClipTopToBottomLeft.Entry, индекс 86
                    #00,                                                        ; SecondSides7, индекс 87 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides8, старший байт @ThreeD.ReturnClipCase.Entry, индекс 88
                    HIGH(@ThreeD.ClipTopToTopRight.Entry),                      ; SecondSides9, старший байт @ThreeD.ClipTopToTopRight.Entry, индекс 89
                    HIGH(@ThreeD.ClipTopToTopLeft.Entry),                       ; SecondSidesA, старший байт @ThreeD.ClipTopToTopLeft.Entry, индекс 8A
                    #00,                                                        ; SecondSidesB, индекс 8B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 8C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 8D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 8E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 8F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides9
FirstSides9:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipTopRightToInside.Entry),                   ; SecondSides0, старший байт @ThreeD.ClipTopRightToInside.Entry, индекс 90
                    HIGH(@ThreeD.ClipTopRightToRight.Entry),                    ; SecondSides1, старший байт @ThreeD.ClipTopRightToRight.Entry, индекс 91
                    HIGH(@ThreeD.ClipTopRightToLeft.Entry),                     ; SecondSides2, старший байт @ThreeD.ClipTopRightToLeft.Entry, индекс 92
                    #00,                                                        ; SecondSides3, индекс 93 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipTopRightToBottom.Entry),                   ; SecondSides4, старший байт @ThreeD.ClipTopRightToBottom.Entry, индекс 94
                    HIGH(@ThreeD.ClipTopRightToBottomRight.Entry),              ; SecondSides5, старший байт @ThreeD.ClipTopRightToBottomRight.Entry, индекс 95
                    HIGH(@ThreeD.ClipTopRightToBottomLeft.Entry),               ; SecondSides6, старший байт @ThreeD.ClipTopRightToBottomLeft.Entry, индекс 96
                    #00,                                                        ; SecondSides7, индекс 97 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipTopRightToTop.Entry),                      ; SecondSides8, старший байт @ThreeD.ClipTopRightToTop.Entry, индекс 98
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSides9, старший байт @ThreeD.ReturnClipCase.Entry, индекс 99
                    HIGH(@ThreeD.ExitClipContour.Entry),                        ; SecondSidesA, старший байт @ThreeD.ExitClipContour.Entry, индекс 9A
                    #00,                                                        ; SecondSidesB, индекс 9B не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 9C не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 9D не получается из 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 9E не получается из 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 9F не получается из 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesA
FirstSidesA:    FClipTargetHighRow {
                    HIGH(@ThreeD.ClipTopLeftToInside.Entry),                    ; SecondSides0, старший байт @ThreeD.ClipTopLeftToInside.Entry, индекс A0
                    HIGH(@ThreeD.ClipTopLeftToRight.Entry),                     ; SecondSides1, старший байт @ThreeD.ClipTopLeftToRight.Entry, индекс A1
                    HIGH(@ThreeD.ClipTopLeftToLeft.Entry),                      ; SecondSides2, старший байт @ThreeD.ClipTopLeftToLeft.Entry, индекс A2
                    #00,                                                        ; SecondSides3, индекс A3 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipTopLeftToBottom.Entry),                    ; SecondSides4, старший байт @ThreeD.ClipTopLeftToBottom.Entry, индекс A4
                    HIGH(@ThreeD.ClipTopLeftToBottomRight.Entry),               ; SecondSides5, старший байт @ThreeD.ClipTopLeftToBottomRight.Entry, индекс A5
                    HIGH(@ThreeD.ExitClipContour.Entry),                        ; SecondSides6, старший байт @ThreeD.ExitClipContour.Entry, индекс A6
                    #00,                                                        ; SecondSides7, индекс A7 не получается из 81 нормальной пары, исходный байт сохранён
                    HIGH(@ThreeD.ClipTopLeftToTop.Entry),                       ; SecondSides8, старший байт @ThreeD.ClipTopLeftToTop.Entry, индекс A8
                    HIGH(@ThreeD.ClipTopLeftToTopRight.Entry),                  ; SecondSides9, старший байт @ThreeD.ClipTopLeftToTopRight.Entry, индекс A9
                    HIGH(@ThreeD.ReturnClipCase.Entry),                         ; SecondSidesA, старший байт @ThreeD.ReturnClipCase.Entry, индекс AA
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
