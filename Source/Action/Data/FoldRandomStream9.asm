                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBE4
                ; -----------------------------------------
                ; исходная физическая запись Stream9
Stream9:        FFoldedRandomState {
                    #00E7,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBE7
                endmodule
