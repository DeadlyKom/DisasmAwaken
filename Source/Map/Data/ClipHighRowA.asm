                module MapClipHighRowA
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DFA0
                ; -----------------------------------------
                ; исходная физическая запись FirstSidesA
FirstSidesA:    FMapClipHighHead {
                    HIGH(@Map.MapClipCases.CaseTL_I),                           ; SecondSides0, старший байт адреса цели для индекса A0
                    HIGH(@Map.MapClipCases.CaseTL_R),                           ; SecondSides1, старший байт адреса цели для индекса A1
                    HIGH(@Map.MapClipCases.CaseTL_L),                           ; SecondSides2, старший байт адреса цели для индекса A2
                    #00,                                                        ; SecondSides3, исходный байт индекса A3 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseTL_B),                           ; SecondSides4, старший байт адреса цели для индекса A4
                    HIGH(@Map.MapClipCases.CaseTL_BR),                          ; SecondSides5, старший байт адреса цели для индекса A5
                    HIGH(@Map.UnwindClipFrame.Entry),                           ; SecondSides6, старший байт адреса цели для индекса A6
                    #00,                                                        ; SecondSides7, исходный байт индекса A7 вне девяти допустимых кодов стороны
                    HIGH(@Map.MapClipCases.CaseTL_T),                           ; SecondSides8, старший байт адреса цели для индекса A8
                    HIGH(@Map.MapClipCases.CaseTL_TR),                          ; SecondSides9, старший байт адреса цели для индекса A9
                    HIGH(@Map.MapClipCases.SameZone)                            ; SecondSidesA, старший байт адреса цели для индекса AA
                }
                assert $ == #DFAB
                endmodule
