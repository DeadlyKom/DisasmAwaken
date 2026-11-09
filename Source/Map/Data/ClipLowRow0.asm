                module MapClipLowRow0
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE00
                ; -----------------------------------------
                ; исходная физическая запись FirstSides0
FirstSides0:    FClipTargetLowHead {
                    LOW(@Map.AppendSecondClipPoint.Entry),                      ; SecondSides0, младший байт адреса цели для индекса 00
                    LOW(@Map.AppendRightClipIntersection.Entry),                ; SecondSides1, младший байт адреса цели для индекса 01
                    LOW(@Map.AppendLeftClipIntersection.Entry),                 ; SecondSides2, младший байт адреса цели для индекса 02
                    #00,                                                        ; SecondSides3, исходный байт индекса 03 вне девяти допустимых кодов стороны
                    LOW(@Map.AppendBottomClipIntersection.Entry),               ; SecondSides4, младший байт адреса цели для индекса 04
                    LOW(@Map.MapClipCases.CaseI_BR),                            ; SecondSides5, младший байт адреса цели для индекса 05
                    LOW(@Map.MapClipCases.CaseI_BL),                            ; SecondSides6, младший байт адреса цели для индекса 06
                    #00,                                                        ; SecondSides7, исходный байт индекса 07 вне девяти допустимых кодов стороны
                    LOW(@Map.AppendTopClipIntersection.Entry),                  ; SecondSides8, младший байт адреса цели для индекса 08
                    LOW(@Map.MapClipCases.CaseI_TR),                            ; SecondSides9, младший байт адреса цели для индекса 09
                    LOW(@Map.MapClipCases.CaseI_TL)                             ; SecondSidesA, младший байт адреса цели для индекса 0A
                }
                assert $ == #DE0B
                endmodule
