                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBF6
                ; -----------------------------------------
                ; исходная физическая запись Stream14
Stream14:       FFoldedRandomState {
                    #030D,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #01                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBF9
                endmodule
