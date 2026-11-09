                module MapClipLowRow6
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE60
                ; -----------------------------------------
                ; исходная физическая запись FirstSides6
FirstSides6:    FClipTargetLowHead {
                    LOW(@Map.MapClipCases.CaseBL_I),                            ; SecondSides0, младший байт адреса цели для индекса 60
                    LOW(@Map.MapClipCases.CaseBL_R),                            ; SecondSides1, младший байт адреса цели для индекса 61
                    LOW(@Map.MapClipCases.CaseBL_L),                            ; SecondSides2, младший байт адреса цели для индекса 62
                    #00,                                                        ; SecondSides3, исходный байт индекса 63 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseBL_B),                            ; SecondSides4, младший байт адреса цели для индекса 64
                    LOW(@Map.UnwindClipFrame.Entry),                            ; SecondSides5, младший байт адреса цели для индекса 65
                    LOW(@Map.MapClipCases.SameZone),                            ; SecondSides6, младший байт адреса цели для индекса 66
                    #00,                                                        ; SecondSides7, исходный байт индекса 67 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseBL_T),                            ; SecondSides8, младший байт адреса цели для индекса 68
                    LOW(@Map.MapClipCases.CaseBL_TR),                           ; SecondSides9, младший байт адреса цели для индекса 69
                    LOW(@Map.MapClipCases.CaseBL_TL)                            ; SecondSidesA, младший байт адреса цели для индекса 6A
                }
                assert $ == #DE6B
                endmodule
