                module ActionByteLimitCounter
                ; Документация [локальные поля контекста](../../../Docs/ActionLocalContextPhysicalData.md)
                assert $ == #9BD2
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FByteLimitCounter {
                    #00,                                                        ; Current, младший байт E, кандидат пополнения увеличивается по модулю 256
                    #28                                                         ; Limit, старший байт D, беззнаковый предел кандидата E
                }
                assert $ == #9BD4
                endmodule
