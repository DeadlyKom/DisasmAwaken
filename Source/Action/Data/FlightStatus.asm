                module ActionFlightStatus
                ; Документация [локальные поля контекста](../../../Docs/ActionLocalContextPhysicalData.md)
                assert $ == #9BCD
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFlightStatus {
                    #00                                                         ; Code, статус игрока, переносится на станцию для сценария штрафов
                }
                assert $ == #9BCE
                endmodule
