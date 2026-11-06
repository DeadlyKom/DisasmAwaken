                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EC05
                ; -----------------------------------------
                ; исходная физическая запись Stream5
Stream5:        FFoldedRandomState {
                    #001D,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EC08
                endmodule
