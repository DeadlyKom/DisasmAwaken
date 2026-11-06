                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBF3
                ; -----------------------------------------
                ; исходная физическая запись Stream13
Stream13:       FFoldedRandomState {
                    #000D,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBF6
                endmodule
