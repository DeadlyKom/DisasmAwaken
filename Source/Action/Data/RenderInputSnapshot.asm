                module ActionRenderInputSnapshot
                ; Документация [состояние переноса и рендера](../../../Docs/MapDistanceAndRenderState.md)
                assert $ == #9B8F
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FRenderInputSnapshot {
                    #0000,                                                      ; InputX, первое исходное слово текущего объекта до допуска по старшему байту
                    #0000,                                                      ; InputY, второе исходное слово после допуска X, до допуска Y
                    #0000                                                       ; InputDepth, третье исходное слово после допуска Y, до допуска глубины
                }
                assert $ == #9B95
                endmodule
