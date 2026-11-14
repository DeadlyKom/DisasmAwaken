                module ActionPreferredByteState
                ; Документация [выбор запаса топлива](../../../Docs/ActionPreferredByte.md)
                assert $ == #9C10
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreferredBytePair {
                    #00,                                                        ; Preferred, топливо МРП, приоритет при ненулевом запасе
                    #14                                                         ; Fallback, топливо ЛНП, выбирается при нуле МРП
                }
                assert $ == #9C12
                endmodule
