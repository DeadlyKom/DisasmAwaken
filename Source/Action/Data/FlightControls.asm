                module ActionFlightControls
                ; Документация [физические входные состояния](../../../Docs/ActionInputContextData.md)
                assert $ == #9B95
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFlightControls {
                    #00,                                                        ; YControl, знаковое байтовое управление проходом Y
                    #00,                                                        ; XControl, знаковое байтовое управление проходом X
                    #00                                                         ; TurnControl, индекс синусоиды получается отрицанием по модулю 256
                }
                assert $ == #9B98
                endmodule
