                module StationMeasuredDistance
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #9908
                ; -----------------------------------------
                ; исходная физическая запись State
State:          FMeasuredDistance {
                    #00                                                         ; Value, результат MeasureCoordinateDistance, FF при переполнении
                }
                assert $ == #9909
                endmodule
