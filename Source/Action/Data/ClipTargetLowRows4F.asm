                module ActionClipTargetLowRows4F
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF40
                ; -----------------------------------------
                ; исходная физическая запись FirstSides4
FirstSides4:    FClipTargetLowRow {
                    LOW(@Action.ClipBottomToInside.Entry),                      ; SecondSides0, младший байт @Action.ClipBottomToInside.Entry, индекс 40
                    LOW(@Action.ClipBottomToRight.Entry),                       ; SecondSides1, младший байт @Action.ClipBottomToRight.Entry, индекс 41
                    LOW(@Action.ClipBottomToLeft.Entry),                        ; SecondSides2, младший байт @Action.ClipBottomToLeft.Entry, индекс 42
                    #00,                                                        ; SecondSides3, индекс 43 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides4, младший байт @Action.ReturnClipCase.Entry, индекс 44
                    LOW(@Action.ClipBottomToBottomRight.Entry),                 ; SecondSides5, младший байт @Action.ClipBottomToBottomRight.Entry, индекс 45
                    LOW(@Action.ClipBottomToBottomLeft.Entry),                  ; SecondSides6, младший байт @Action.ClipBottomToBottomLeft.Entry, индекс 46
                    #00,                                                        ; SecondSides7, индекс 47 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipBottomToTop.Entry),                         ; SecondSides8, младший байт @Action.ClipBottomToTop.Entry, индекс 48
                    LOW(@Action.ClipBottomToTopRight.Entry),                    ; SecondSides9, младший байт @Action.ClipBottomToTopRight.Entry, индекс 49
                    LOW(@Action.ClipBottomToTopLeft.Entry),                     ; SecondSidesA, младший байт @Action.ClipBottomToTopLeft.Entry, индекс 4A
                    #00,                                                        ; SecondSidesB, индекс 4B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 4C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 4D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 4E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 4F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides5
FirstSides5:    FClipTargetLowRow {
                    LOW(@Action.ClipBottomRightToInside.Entry),                 ; SecondSides0, младший байт @Action.ClipBottomRightToInside.Entry, индекс 50
                    LOW(@Action.ClipBottomRightToRight.Entry),                  ; SecondSides1, младший байт @Action.ClipBottomRightToRight.Entry, индекс 51
                    LOW(@Action.ClipBottomRightToLeft.Entry),                   ; SecondSides2, младший байт @Action.ClipBottomRightToLeft.Entry, индекс 52
                    #00,                                                        ; SecondSides3, индекс 53 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipBottomRightToBottom.Entry),                 ; SecondSides4, младший байт @Action.ClipBottomRightToBottom.Entry, индекс 54
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides5, младший байт @Action.ReturnClipCase.Entry, индекс 55
                    LOW(@Action.ClipBottomRightToBottomLeft.Entry),             ; SecondSides6, младший байт @Action.ClipBottomRightToBottomLeft.Entry, индекс 56
                    #00,                                                        ; SecondSides7, индекс 57 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipBottomRightToTop.Entry),                    ; SecondSides8, младший байт @Action.ClipBottomRightToTop.Entry, индекс 58
                    LOW(@Action.ExitClipContour.Entry),                         ; SecondSides9, младший байт @Action.ExitClipContour.Entry, индекс 59
                    LOW(@Action.ClipBottomRightToTopLeft.Entry),                ; SecondSidesA, младший байт @Action.ClipBottomRightToTopLeft.Entry, индекс 5A
                    #00,                                                        ; SecondSidesB, индекс 5B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 5C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 5D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 5E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 5F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides6
FirstSides6:    FClipTargetLowRow {
                    LOW(@Action.ClipBottomLeftToInside.Entry),                  ; SecondSides0, младший байт @Action.ClipBottomLeftToInside.Entry, индекс 60
                    LOW(@Action.ClipBottomLeftToRight.Entry),                   ; SecondSides1, младший байт @Action.ClipBottomLeftToRight.Entry, индекс 61
                    LOW(@Action.ClipBottomLeftToLeft.Entry),                    ; SecondSides2, младший байт @Action.ClipBottomLeftToLeft.Entry, индекс 62
                    #00,                                                        ; SecondSides3, индекс 63 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipBottomLeftToBottom.Entry),                  ; SecondSides4, младший байт @Action.ClipBottomLeftToBottom.Entry, индекс 64
                    LOW(@Action.ExitClipContour.Entry),                         ; SecondSides5, младший байт @Action.ExitClipContour.Entry, индекс 65
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides6, младший байт @Action.ReturnClipCase.Entry, индекс 66
                    #00,                                                        ; SecondSides7, индекс 67 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipBottomLeftToTop.Entry),                     ; SecondSides8, младший байт @Action.ClipBottomLeftToTop.Entry, индекс 68
                    LOW(@Action.ClipBottomLeftToTopRight.Entry),                ; SecondSides9, младший байт @Action.ClipBottomLeftToTopRight.Entry, индекс 69
                    LOW(@Action.ClipBottomLeftToTopLeft.Entry),                 ; SecondSidesA, младший байт @Action.ClipBottomLeftToTopLeft.Entry, индекс 6A
                    #00,                                                        ; SecondSidesB, индекс 6B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 6C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 6D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 6E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 6F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides7
FirstSides7:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс 70 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс 71 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс 72 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс 73 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс 74 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс 75 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс 76 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс 77 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс 78 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс 79 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс 7A вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс 7B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 7C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 7D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 7E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 7F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides8
FirstSides8:    FClipTargetLowRow {
                    LOW(@Action.ClipTopToInside.Entry),                         ; SecondSides0, младший байт @Action.ClipTopToInside.Entry, индекс 80
                    LOW(@Action.ClipTopToRight.Entry),                          ; SecondSides1, младший байт @Action.ClipTopToRight.Entry, индекс 81
                    LOW(@Action.ClipTopToLeft.Entry),                           ; SecondSides2, младший байт @Action.ClipTopToLeft.Entry, индекс 82
                    #00,                                                        ; SecondSides3, индекс 83 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipTopToBottom.Entry),                         ; SecondSides4, младший байт @Action.ClipTopToBottom.Entry, индекс 84
                    LOW(@Action.ClipTopToBottomRight.Entry),                    ; SecondSides5, младший байт @Action.ClipTopToBottomRight.Entry, индекс 85
                    LOW(@Action.ClipTopToBottomLeft.Entry),                     ; SecondSides6, младший байт @Action.ClipTopToBottomLeft.Entry, индекс 86
                    #00,                                                        ; SecondSides7, индекс 87 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides8, младший байт @Action.ReturnClipCase.Entry, индекс 88
                    LOW(@Action.ClipTopToTopRight.Entry),                       ; SecondSides9, младший байт @Action.ClipTopToTopRight.Entry, индекс 89
                    LOW(@Action.ClipTopToTopLeft.Entry),                        ; SecondSidesA, младший байт @Action.ClipTopToTopLeft.Entry, индекс 8A
                    #00,                                                        ; SecondSidesB, индекс 8B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 8C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 8D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 8E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 8F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides9
FirstSides9:    FClipTargetLowRow {
                    LOW(@Action.ClipTopRightToInside.Entry),                    ; SecondSides0, младший байт @Action.ClipTopRightToInside.Entry, индекс 90
                    LOW(@Action.ClipTopRightToRight.Entry),                     ; SecondSides1, младший байт @Action.ClipTopRightToRight.Entry, индекс 91
                    LOW(@Action.ClipTopRightToLeft.Entry),                      ; SecondSides2, младший байт @Action.ClipTopRightToLeft.Entry, индекс 92
                    #00,                                                        ; SecondSides3, индекс 93 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipTopRightToBottom.Entry),                    ; SecondSides4, младший байт @Action.ClipTopRightToBottom.Entry, индекс 94
                    LOW(@Action.ClipTopRightToBottomRight.Entry),               ; SecondSides5, младший байт @Action.ClipTopRightToBottomRight.Entry, индекс 95
                    LOW(@Action.ClipTopRightToBottomLeft.Entry),                ; SecondSides6, младший байт @Action.ClipTopRightToBottomLeft.Entry, индекс 96
                    #00,                                                        ; SecondSides7, индекс 97 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipTopRightToTop.Entry),                       ; SecondSides8, младший байт @Action.ClipTopRightToTop.Entry, индекс 98
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSides9, младший байт @Action.ReturnClipCase.Entry, индекс 99
                    LOW(@Action.ExitClipContour.Entry),                         ; SecondSidesA, младший байт @Action.ExitClipContour.Entry, индекс 9A
                    #00,                                                        ; SecondSidesB, индекс 9B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 9C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 9D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 9E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 9F вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesA
FirstSidesA:    FClipTargetLowRow {
                    LOW(@Action.ClipTopLeftToInside.Entry),                     ; SecondSides0, младший байт @Action.ClipTopLeftToInside.Entry, индекс A0
                    LOW(@Action.ClipTopLeftToRight.Entry),                      ; SecondSides1, младший байт @Action.ClipTopLeftToRight.Entry, индекс A1
                    LOW(@Action.ClipTopLeftToLeft.Entry),                       ; SecondSides2, младший байт @Action.ClipTopLeftToLeft.Entry, индекс A2
                    #00,                                                        ; SecondSides3, индекс A3 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipTopLeftToBottom.Entry),                     ; SecondSides4, младший байт @Action.ClipTopLeftToBottom.Entry, индекс A4
                    LOW(@Action.ClipTopLeftToBottomRight.Entry),                ; SecondSides5, младший байт @Action.ClipTopLeftToBottomRight.Entry, индекс A5
                    LOW(@Action.ExitClipContour.Entry),                         ; SecondSides6, младший байт @Action.ExitClipContour.Entry, индекс A6
                    #00,                                                        ; SecondSides7, индекс A7 вне 81 нормальной пары, исходный байт сохранён
                    LOW(@Action.ClipTopLeftToTop.Entry),                        ; SecondSides8, младший байт @Action.ClipTopLeftToTop.Entry, индекс A8
                    LOW(@Action.ClipTopLeftToTopRight.Entry),                   ; SecondSides9, младший байт @Action.ClipTopLeftToTopRight.Entry, индекс A9
                    LOW(@Action.ReturnClipCase.Entry),                          ; SecondSidesA, младший байт @Action.ReturnClipCase.Entry, индекс AA
                    #00,                                                        ; SecondSidesB, индекс AB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс AC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс AD вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс AE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс AF вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesB
FirstSidesB:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс B0 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс B1 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс B2 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс B3 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс B4 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс B5 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс B6 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс B7 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс B8 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс B9 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс BA вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс BB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс BC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс BD вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс BE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс BF вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesC
FirstSidesC:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс C0 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс C1 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс C2 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс C3 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс C4 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс C5 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс C6 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс C7 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс C8 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс C9 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс CA вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс CB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс CC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс CD вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс CE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс CF вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesD
FirstSidesD:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс D0 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс D1 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс D2 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс D3 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс D4 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс D5 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс D6 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс D7 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс D8 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс D9 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс DA вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс DB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс DC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс DD вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс DE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс DF вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesE
FirstSidesE:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс E0 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс E1 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс E2 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс E3 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс E4 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс E5 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс E6 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс E7 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс E8 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс E9 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс EA вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс EB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс EC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс ED вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс EE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс EF вне 81 нормальной пары, исходный байт сохранён
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesF
FirstSidesF:    FClipTargetLowRow {
                    #00,                                                        ; SecondSides0, индекс F0 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides1, индекс F1 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides2, индекс F2 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides3, индекс F3 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides4, индекс F4 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides5, индекс F5 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides6, индекс F6 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides7, индекс F7 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides8, индекс F8 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSides9, индекс F9 вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesA, индекс FA вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesB, индекс FB вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс FC вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс FD вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс FE вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс FF вне 81 нормальной пары, исходный байт сохранён
                }
                assert $ == #D000
                endmodule
