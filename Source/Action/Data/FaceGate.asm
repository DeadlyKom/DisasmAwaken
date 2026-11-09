                module ActionFaceGate
                ; Документация [рабочие слова текущего отсечения](../../../Docs/ActionClippedLineWorkData.md)
                assert $ == #8D5A
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFaceGateCode {
                    #00                                                         ; Code, полный код ориентации, ноль допускает связанную ломаную, любой ненулевой байт запрещает
                }
                assert $ == #8D5B
                endmodule
