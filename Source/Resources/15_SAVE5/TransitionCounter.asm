                module Save5TransitionCounter
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #00CB
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FTransitionCounter {
                    #00                                                         ; Count, байтовый счётчик, станционный переход условно прибавляет 30
                }
                assert $ == #00CC
                endmodule
