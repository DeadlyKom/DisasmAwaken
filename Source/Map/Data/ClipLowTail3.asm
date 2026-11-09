                module MapClipLowTail3
                ; Документация [страницы диспетчера отсечения KARTA](../../../Docs/MapClipTablePages.md)
                assert $ == #DE3E
                ; -----------------------------------------
                ; исходная физическая запись First3Tail
First3Tail:     FMapClipLowTail3 {
                    #00,                                                        ; SecondSidesE, исходный байт индекса 3E вне девяти допустимых кодов стороны
                    #00                                                         ; SecondSidesF, исходный байт индекса 3F вне девяти допустимых кодов стороны
                }
                assert $ == #DE40
                endmodule
