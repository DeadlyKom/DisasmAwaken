                module MapClipLowRow2
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE20
                ; -----------------------------------------
                ; исходная физическая запись FirstSides2
FirstSides2:    FClipTargetLowHead {
                    LOW(@Map.MapClipCases.CaseL_I),                             ; SecondSides0, младший байт адреса цели для индекса 20
                    LOW(@Map.MapClipCases.CaseL_R),                             ; SecondSides1, младший байт адреса цели для индекса 21
                    LOW(@Map.MapClipCases.SameZone),                            ; SecondSides2, младший байт адреса цели для индекса 22
                    #00,                                                        ; SecondSides3, исходный байт индекса 23 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseL_B),                             ; SecondSides4, младший байт адреса цели для индекса 24
                    LOW(@Map.MapClipCases.CaseL_BR),                            ; SecondSides5, младший байт адреса цели для индекса 25
                    LOW(@Map.MapClipCases.CaseL_BL),                            ; SecondSides6, младший байт адреса цели для индекса 26
                    #00,                                                        ; SecondSides7, исходный байт индекса 27 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseL_T),                             ; SecondSides8, младший байт адреса цели для индекса 28
                    LOW(@Map.MapClipCases.CaseL_TR),                            ; SecondSides9, младший байт адреса цели для индекса 29
                    LOW(@Map.MapClipCases.CaseL_TL)                             ; SecondSidesA, младший байт адреса цели для индекса 2A
                }
                assert $ == #DE2B
                endmodule
