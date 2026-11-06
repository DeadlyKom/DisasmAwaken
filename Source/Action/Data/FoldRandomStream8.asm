                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBE1
                ; -----------------------------------------
                ; исходная физическая запись Stream8
Stream8:        FFoldedRandomState {
                    #0009,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBE4
                endmodule
