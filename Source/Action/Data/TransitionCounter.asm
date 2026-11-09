                module ActionTransitionCounter
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #9C88
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FTransitionCounter {
                    #64                                                         ; Count, байтовый счётчик, станционный переход условно прибавляет 30
                }
                assert $ == #9C89
                endmodule
