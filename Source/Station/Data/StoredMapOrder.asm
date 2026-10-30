                module StoredMapOrder
; Документация [количество и порядок второго списка](../../../Docs/SecondaryPointOrder.md)
; Потребитель [открытая цепочка и код режима](../../../Docs/MapPointChain.md)
                assert $ == #9970
Entry:          FStoredMapOrder {
                    #22,                                                        ; FStoredMapOrder.Layout, N=2, режим Xor, биты 7..6 нулевые
                    #00,                                                        ; FStoredMapOrder.Order00
                    #00,                                                        ; FStoredMapOrder.Order01
                    #00,                                                        ; FStoredMapOrder.Order02
                    #00,                                                        ; FStoredMapOrder.Order03
                    #00,                                                        ; FStoredMapOrder.Order04
                    #00,                                                        ; FStoredMapOrder.Order05
                    #00,                                                        ; FStoredMapOrder.Order06
                    #00,                                                        ; FStoredMapOrder.Order07
                    #00,                                                        ; FStoredMapOrder.Order08
                    #00                                                         ; FStoredMapOrder.Order09
                }
                assert $ == #997B
                endmodule
