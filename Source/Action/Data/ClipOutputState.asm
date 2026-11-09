                module ActionClipOutputState
                ; Документация [поля очереди и параметров](../../../Docs/ActionQueueParameterPhysicalData.md)
                assert $ == #9BA3
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FClipOutputState {
                    #00                                                         ; OutputSize, байтовая длина выходных пар Second, First в странице 90
                }
                assert $ == #9BA4
                endmodule
