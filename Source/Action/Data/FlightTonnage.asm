                module ActionFlightTonnage
                ; Документация [локальные поля контекста](../../../Docs/ActionLocalContextPhysicalData.md)
                assert $ == #9BD2
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFlightTonnage {
                    #00,                                                        ; Used, учтённый тоннаж, изменяется в полёте по модулю 256
                    #28                                                         ; Capacity, беззнаковый предел при пополнении топлива и подборе
                }
                assert $ == #9BD4
                endmodule
