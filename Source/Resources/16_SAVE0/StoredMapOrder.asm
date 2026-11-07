                module Save0StoredMapOrder
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0135
Entry:          FStoredMapOrder {
                    #22,                                                        ; FStoredMapOrder.Layout, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order00, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order01, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order02, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order03, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order04, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order05, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order06, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order07, значение дискового слота
                    #00,                                                        ; FStoredMapOrder.Order08, значение дискового слота
                    #00                                                         ; FStoredMapOrder.Order09, значение дискового слота
                }
                assert $ == #0140
                endmodule
