                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBDE
                ; -----------------------------------------
                ; исходная физическая запись Stream0
Stream0:        FFoldedRandomState {
                    #0065,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBE1
                endmodule
