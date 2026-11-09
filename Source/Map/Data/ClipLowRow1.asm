                module MapClipLowRow1
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE10
                ; -----------------------------------------
                ; исходная физическая запись FirstSides1
FirstSides1:    FClipTargetLowHead {
                    LOW(@Map.MapClipCases.CaseR_I),                             ; SecondSides0, младший байт адреса цели для индекса 10
                    LOW(@Map.MapClipCases.SameZone),                            ; SecondSides1, младший байт адреса цели для индекса 11
                    LOW(@Map.MapClipCases.CaseR_L),                             ; SecondSides2, младший байт адреса цели для индекса 12
                    #00,                                                        ; SecondSides3, исходный байт индекса 13 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseR_B),                             ; SecondSides4, младший байт адреса цели для индекса 14
                    LOW(@Map.MapClipCases.CaseR_BR),                            ; SecondSides5, младший байт адреса цели для индекса 15
                    LOW(@Map.MapClipCases.CaseR_BL),                            ; SecondSides6, младший байт адреса цели для индекса 16
                    #00,                                                        ; SecondSides7, исходный байт индекса 17 вне девяти допустимых кодов стороны
                    LOW(@Map.MapClipCases.CaseR_T),                             ; SecondSides8, младший байт адреса цели для индекса 18
                    LOW(@Map.MapClipCases.CaseR_TR),                            ; SecondSides9, младший байт адреса цели для индекса 19
                    LOW(@Map.MapClipCases.CaseR_TL)                             ; SecondSidesA, младший байт адреса цели для индекса 1A
                }
                assert $ == #DE1B
                endmodule
