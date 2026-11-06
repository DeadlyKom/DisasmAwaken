                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBF9
                ; -----------------------------------------
                ; исходная физическая запись Stream6
Stream6:        FFoldedRandomState {
                    #002C,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBFC
                endmodule
