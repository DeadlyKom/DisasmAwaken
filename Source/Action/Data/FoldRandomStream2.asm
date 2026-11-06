                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBEA
                ; -----------------------------------------
                ; исходная физическая запись Stream2
Stream2:        FFoldedRandomState {
                    #000A,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBED
                endmodule
