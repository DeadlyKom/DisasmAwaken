                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBFC
                ; -----------------------------------------
                ; исходная физическая запись Stream7
Stream7:        FFoldedRandomState {
                    #0015,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBFF
                endmodule
