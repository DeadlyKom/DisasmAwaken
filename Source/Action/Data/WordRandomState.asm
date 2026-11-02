                module ActionWordRandomState
                ; Документация [двухсловный генератор](../../../Docs/ControlsWordRandom.md)
                assert $ == #9B15
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FWordRandomState {
                    #0000,                                                      ; First, исходное первое слово генератора, обновляется прежним Second
                    #0000                                                       ; Second, исходное второе слово генератора, обновляется смешивающей рекурсией
                }
                assert $ == #9B19
                endmodule
