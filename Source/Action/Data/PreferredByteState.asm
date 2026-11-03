                module ActionPreferredByteState
                ; Документация [выбор байта с приоритетом](../../../Docs/ActionPreferredByte.md)
                assert $ == #9C10
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreferredBytePair {
                    #00,                                                        ; Preferred, выбирается вместе со своим адресом, если байт ненулевой
                    #14                                                         ; Fallback, выбирается вместе со своим адресом, если Preferred равен нулю
                }
                assert $ == #9C12
                endmodule
