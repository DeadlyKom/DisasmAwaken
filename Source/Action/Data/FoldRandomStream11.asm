                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBED
                ; -----------------------------------------
                ; исходная физическая запись Stream11
Stream11:       FFoldedRandomState {
                    #014D,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBF0
                endmodule
