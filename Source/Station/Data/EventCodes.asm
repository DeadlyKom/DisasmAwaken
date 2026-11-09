                module StationEventCodes
                ; Документация [физические поля и потребители](../../../Docs/InterfaceEventAndSpecialRecord.md)
                assert $ == #9839
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FStationEventCodes {
                    #00,                                                        ; InterfaceCode, код интерфейсного события, используется при передаче действия и выборе меню
                    #00                                                         ; ScriptCode, код события для LANG, ReadEventCode переносит его в стек выражений
                }
                assert $ == #983B
                endmodule
