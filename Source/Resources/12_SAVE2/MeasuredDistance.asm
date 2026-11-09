                module Save2MeasuredDistance
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #00CD
                ; -----------------------------------------
                ; исходная физическая запись State
State:          FMeasuredDistance {
                    #00                                                         ; Value, результат MeasureCoordinateDistance, FF при переполнении
                }
                assert $ == #00CE
                endmodule
