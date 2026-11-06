                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBFF
                ; -----------------------------------------
                ; исходная физическая запись Stream4
Stream4:        FFoldedRandomState {
                    #00F7,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EC02
                endmodule
