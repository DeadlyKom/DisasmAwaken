                module MapClipLowRows45
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE40
                ; -----------------------------------------
                ; исходная физическая запись FirstSides4
FirstSides4:    FClipTargetLowRow {
                    LOW(@Map.MapClipCases.CaseB_I),                             ; SecondSides0, младший байт адреса цели для индекса 40
                    LOW(@Map.MapClipCases.CaseB_R),                             ; SecondSides1, младший байт адреса цели для индекса 41
                    LOW(@Map.MapClipCases.CaseB_L),                             ; SecondSides2, младший байт адреса цели для индекса 42
                    #00,                                                        ; SecondSides3, исходный байт индекса 43 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.SameZone),                            ; SecondSides4, младший байт адреса цели для индекса 44
                    LOW(@Map.MapClipCases.CaseB_BR),                            ; SecondSides5, младший байт адреса цели для индекса 45
                    LOW(@Map.MapClipCases.CaseB_BL),                            ; SecondSides6, младший байт адреса цели для индекса 46
                    #00,                                                        ; SecondSides7, исходный байт индекса 47 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseB_T),                             ; SecondSides8, младший байт адреса цели для индекса 48
                    LOW(@Map.MapClipCases.CaseB_TR),                            ; SecondSides9, младший байт адреса цели для индекса 49
                    LOW(@Map.MapClipCases.CaseB_TL),                            ; SecondSidesA, младший байт адреса цели для индекса 4A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 4B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 4C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 4D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 4E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 4F вне девяти допустимых кодов стороны
                }
                ; -----------------------------------------
                ; исходная физическая запись FirstSides5
FirstSides5:    FClipTargetLowRow {
                    LOW(@Map.MapClipCases.CaseBR_I),                            ; SecondSides0, младший байт адреса цели для индекса 50
                    LOW(@Map.MapClipCases.CaseBR_R),                            ; SecondSides1, младший байт адреса цели для индекса 51
                    LOW(@Map.MapClipCases.CaseBR_L),                            ; SecondSides2, младший байт адреса цели для индекса 52
                    #00,                                                        ; SecondSides3, исходный байт индекса 53 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseBR_B),                            ; SecondSides4, младший байт адреса цели для индекса 54
                    LOW(@Map.MapClipCases.SameZone),                            ; SecondSides5, младший байт адреса цели для индекса 55
                    LOW(@Map.MapClipCases.CaseBR_BL),                           ; SecondSides6, младший байт адреса цели для индекса 56
                    #00,                                                        ; SecondSides7, исходный байт индекса 57 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseBR_T),                            ; SecondSides8, младший байт адреса цели для индекса 58
                    LOW(@Map.UnwindClipFrame.Entry),                            ; SecondSides9, младший байт адреса цели для индекса 59
                    LOW(@Map.MapClipCases.CaseBR_TL),                           ; SecondSidesA, младший байт адреса цели для индекса 5A
                    #00,                                                        ; SecondSidesB, исходный байт индекса 5B вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesC, исходный байт индекса 5C вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesD, исходный байт индекса 5D вне девяти допустимых кодов стороны
                    #00,                                                        ; SecondSidesE, исходный байт индекса 5E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 5F вне девяти допустимых кодов стороны
                }
                assert $ == #DE60
                endmodule
