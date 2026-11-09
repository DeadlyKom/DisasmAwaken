                module StationTransitionCounter
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #9906
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FTransitionCounter {
                    #64                                                         ; Count, байтовый счётчик, станционный переход условно прибавляет 30
                }
                assert $ == #9907
                endmodule
