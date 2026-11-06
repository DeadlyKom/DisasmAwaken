                module ActionRandomStreams
                ; Документация [генератор со свёрткой переносов](../../../Docs/ActionFoldedRandom.md)
                assert $ == #EBE7
                ; -----------------------------------------
                ; исходная физическая запись Stream10
Stream10:       FFoldedRandomState {
                    #0147,                                                      ; LowWord, младшее слово смешивающей рекурсии
                    #00                                                         ; FoldByte, байт свёртки переносов, числовое состояние, не набор флагов
                }
                assert $ == #EBEA
                endmodule
