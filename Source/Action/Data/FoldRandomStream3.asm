                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBDB
                ; -----------------------------------------
                ; исходная физическая запись Stream3
Stream3:        FFoldedRandomState {
                    #0807,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBDE
                endmodule
