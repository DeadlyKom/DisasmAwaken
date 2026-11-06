                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBF0
                ; -----------------------------------------
                ; исходная физическая запись Stream12
Stream12:       FFoldedRandomState {
                    #00C8,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBF3
                endmodule
