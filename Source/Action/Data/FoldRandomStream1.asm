                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EC02
                ; -----------------------------------------
                ; исходная физическая запись Stream1
Stream1:        FFoldedRandomState {
                    #005D,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EC05
                endmodule
