                module MapClipHighRows09
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DF00
                ; -----------------------------------------
                ; исходная физическая запись FirstSides0
FirstSides0:    FClipTargetHighRow {
                    HIGH(@Map.AppendSecondClipPoint.Entry),                     ; SecondSides0, старший байт адреса цели для индекса 00
                    HIGH(@Map.AppendRightClipIntersection.Entry),               ; SecondSides1, старший байт адреса цели для индекса 01
                    HIGH(@Map.AppendLeftClipIntersection.Entry),                ; SecondSides2, старший байт адреса цели для индекса 02
                    #00,                                                        ; SecondSides3, исходный байт индекса 03 вне девяти допустимых кодов стороны
                    HIGH(@Map.AppendBottomClipIntersection.Entry),              ; SecondSides4, старший байт адреса цели для индекса 04
                    HIGH(@Map.MapClipCases.CaseI_BR),                           ; SecondSides5, старший байт адреса цели для индекса 05
                    HIGH(@Map.MapClipCases.CaseI_BL),                           ; SecondSides6, старший байт адреса цели для индекса 06
                    #00,                                                        ; SecondSides7, исходный байт индекса 07 вне девяти допустимых кодов стороны
                    HIGH(@Map.AppendTopClipIntersection.Entry),                 ; SecondSides8, старший байт адреса цели для индекса 08
                    HIGH(@Map.MapClipCases.CaseI_TR),                           ; SecondSides9, старший байт адреса цели для индекса 09
                    HIGH(@Map.MapClipCases.CaseI_TL),                           ; SecondSidesA, старший байт адреса цели для индекса 0A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 0B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 0C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 0D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 0E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 0F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseR_I),                            ; SecondSides0, старший байт адреса цели для индекса 10
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides1, старший байт адреса цели для индекса 11
                    HIGH(@Map.MapClipCases.CaseR_L),                            ; SecondSides2, старший байт адреса цели для индекса 12
                    #00,                                                        ; SecondSides3, исходный байт индекса 13 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseR_B),                            ; SecondSides4, старший байт адреса цели для индекса 14
                    HIGH(@Map.MapClipCases.CaseR_BR),                           ; SecondSides5, старший байт адреса цели для индекса 15
                    HIGH(@Map.MapClipCases.CaseR_BL),                           ; SecondSides6, старший байт адреса цели для индекса 16
                    #00,                                                        ; SecondSides7, исходный байт индекса 17 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseR_T),                            ; SecondSides8, старший байт адреса цели для индекса 18
                    HIGH(@Map.MapClipCases.CaseR_TR),                           ; SecondSides9, старший байт адреса цели для индекса 19
                    HIGH(@Map.MapClipCases.CaseR_TL),                           ; SecondSidesA, старший байт адреса цели для индекса 1A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 1B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 1C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 1D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 1E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 1F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseL_I),                            ; SecondSides0, старший байт адреса цели для индекса 20
                    HIGH(@Map.MapClipCases.CaseL_R),                            ; SecondSides1, старший байт адреса цели для индекса 21
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides2, старший байт адреса цели для индекса 22
                    #00,                                                        ; SecondSides3, исходный байт индекса 23 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseL_B),                            ; SecondSides4, старший байт адреса цели для индекса 24
                    HIGH(@Map.MapClipCases.CaseL_BR),                           ; SecondSides5, старший байт адреса цели для индекса 25
                    HIGH(@Map.MapClipCases.CaseL_BL),                           ; SecondSides6, старший байт адреса цели для индекса 26
                    #00,                                                        ; SecondSides7, исходный байт индекса 27 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseL_T),                            ; SecondSides8, старший байт адреса цели для индекса 28
                    HIGH(@Map.MapClipCases.CaseL_TR),                           ; SecondSides9, старший байт адреса цели для индекса 29
                    HIGH(@Map.MapClipCases.CaseL_TL),                           ; SecondSidesA, старший байт адреса цели для индекса 2A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 2B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 2C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 2D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 2E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 2F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides3
FirstSides3:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, исходный байт индекса 30 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides1, исходный байт индекса 31 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides2, исходный байт индекса 32 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides3, исходный байт индекса 33 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides4, исходный байт индекса 34 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides5, исходный байт индекса 35 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides6, исходный байт индекса 36 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides7, исходный байт индекса 37 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides8, исходный байт индекса 38 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides9, исходный байт индекса 39 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesA, исходный байт индекса 3A вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesB, исходный байт индекса 3B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 3C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 3D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 3E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 3F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides4
FirstSides4:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseB_I),                            ; SecondSides0, старший байт адреса цели для индекса 40
                    HIGH(@Map.MapClipCases.CaseB_R),                            ; SecondSides1, старший байт адреса цели для индекса 41
                    HIGH(@Map.MapClipCases.CaseB_L),                            ; SecondSides2, старший байт адреса цели для индекса 42
                    #00,                                                        ; SecondSides3, исходный байт индекса 43 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides4, старший байт адреса цели для индекса 44
                    HIGH(@Map.MapClipCases.CaseB_BR),                           ; SecondSides5, старший байт адреса цели для индекса 45
                    HIGH(@Map.MapClipCases.CaseB_BL),                           ; SecondSides6, старший байт адреса цели для индекса 46
                    #00,                                                        ; SecondSides7, исходный байт индекса 47 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseB_T),                            ; SecondSides8, старший байт адреса цели для индекса 48
                    HIGH(@Map.MapClipCases.CaseB_TR),                           ; SecondSides9, старший байт адреса цели для индекса 49
                    HIGH(@Map.MapClipCases.CaseB_TL),                           ; SecondSidesA, старший байт адреса цели для индекса 4A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 4B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 4C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 4D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 4E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 4F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides5
FirstSides5:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseBR_I),                           ; SecondSides0, старший байт адреса цели для индекса 50
                    HIGH(@Map.MapClipCases.CaseBR_R),                           ; SecondSides1, старший байт адреса цели для индекса 51
                    HIGH(@Map.MapClipCases.CaseBR_L),                           ; SecondSides2, старший байт адреса цели для индекса 52
                    #00,                                                        ; SecondSides3, исходный байт индекса 53 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseBR_B),                           ; SecondSides4, старший байт адреса цели для индекса 54
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides5, старший байт адреса цели для индекса 55
                    HIGH(@Map.MapClipCases.CaseBR_BL),                          ; SecondSides6, старший байт адреса цели для индекса 56
                    #00,                                                        ; SecondSides7, исходный байт индекса 57 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseBR_T),                           ; SecondSides8, старший байт адреса цели для индекса 58
                    HIGH(@Map.UnwindClipFrame.Entry),                           ; SecondSides9, старший байт адреса цели для индекса 59
                    HIGH(@Map.MapClipCases.CaseBR_TL),                          ; SecondSidesA, старший байт адреса цели для индекса 5A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 5B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 5C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 5D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 5E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 5F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides6
FirstSides6:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseBL_I),                           ; SecondSides0, старший байт адреса цели для индекса 60
                    HIGH(@Map.MapClipCases.CaseBL_R),                           ; SecondSides1, старший байт адреса цели для индекса 61
                    HIGH(@Map.MapClipCases.CaseBL_L),                           ; SecondSides2, старший байт адреса цели для индекса 62
                    #00,                                                        ; SecondSides3, исходный байт индекса 63 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseBL_B),                           ; SecondSides4, старший байт адреса цели для индекса 64
                    HIGH(@Map.UnwindClipFrame.Entry),                           ; SecondSides5, старший байт адреса цели для индекса 65
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides6, старший байт адреса цели для индекса 66
                    #00,                                                        ; SecondSides7, исходный байт индекса 67 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseBL_T),                           ; SecondSides8, старший байт адреса цели для индекса 68
                    HIGH(@Map.MapClipCases.CaseBL_TR),                          ; SecondSides9, старший байт адреса цели для индекса 69
                    HIGH(@Map.MapClipCases.CaseBL_TL),                          ; SecondSidesA, старший байт адреса цели для индекса 6A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 6B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 6C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 6D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 6E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 6F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides7
FirstSides7:    FClipTargetHighRow {
                    #00,                                                        ; SecondSides0, исходный байт индекса 70 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides1, исходный байт индекса 71 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides2, исходный байт индекса 72 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides3, исходный байт индекса 73 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides4, исходный байт индекса 74 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides5, исходный байт индекса 75 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides6, исходный байт индекса 76 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides7, исходный байт индекса 77 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides8, исходный байт индекса 78 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSides9, исходный байт индекса 79 вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesA, исходный байт индекса 7A вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesB, исходный байт индекса 7B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 7C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 7D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 7E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 7F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides8
FirstSides8:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseT_I),                            ; SecondSides0, старший байт адреса цели для индекса 80
                    HIGH(@Map.MapClipCases.CaseT_R),                            ; SecondSides1, старший байт адреса цели для индекса 81
                    HIGH(@Map.MapClipCases.CaseT_L),                            ; SecondSides2, старший байт адреса цели для индекса 82
                    #00,                                                        ; SecondSides3, исходный байт индекса 83 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseT_B),                            ; SecondSides4, старший байт адреса цели для индекса 84
                    HIGH(@Map.MapClipCases.CaseT_BR),                           ; SecondSides5, старший байт адреса цели для индекса 85
                    HIGH(@Map.MapClipCases.CaseT_BL),                           ; SecondSides6, старший байт адреса цели для индекса 86
                    #00,                                                        ; SecondSides7, исходный байт индекса 87 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides8, старший байт адреса цели для индекса 88
                    HIGH(@Map.MapClipCases.CaseT_TR),                           ; SecondSides9, старший байт адреса цели для индекса 89
                    HIGH(@Map.MapClipCases.CaseT_TL),                           ; SecondSidesA, старший байт адреса цели для индекса 8A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 8B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 8C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 8D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 8E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 8F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides9
FirstSides9:    FClipTargetHighRow {
                    HIGH(@Map.MapClipCases.CaseTR_I),                           ; SecondSides0, старший байт адреса цели для индекса 90
                    HIGH(@Map.MapClipCases.CaseTR_R),                           ; SecondSides1, старший байт адреса цели для индекса 91
                    HIGH(@Map.MapClipCases.CaseTR_L),                           ; SecondSides2, старший байт адреса цели для индекса 92
                    #00,                                                        ; SecondSides3, исходный байт индекса 93 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseTR_B),                           ; SecondSides4, старший байт адреса цели для индекса 94
                    HIGH(@Map.MapClipCases.CaseTR_BR),                          ; SecondSides5, старший байт адреса цели для индекса 95
                    HIGH(@Map.MapClipCases.CaseTR_BL),                          ; SecondSides6, старший байт адреса цели для индекса 96
                    #00,                                                        ; SecondSides7, исходный байт индекса 97 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseTR_T),                           ; SecondSides8, старший байт адреса цели для индекса 98
                    HIGH(@Map.MapClipCases.SameZone),                           ; SecondSides9, старший байт адреса цели для индекса 99
                    HIGH(@Map.UnwindClipFrame.Entry),                           ; SecondSidesA, старший байт адреса цели для индекса 9A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 9B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 9C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 9D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 9E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 9F вне девяти допустимых кодов стороны
                }
                assert $ == #DFA0
                endmodule
