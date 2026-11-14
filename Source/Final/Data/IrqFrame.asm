                module FinalIrqFrame
                ; Документация [временный стек прерывания](../../../Docs/FinalCycle.md)
                assert $ == #6192
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFinalIrqFrame {
                    #0000,                                                      ; SavedAF, слово альтернативного AF после обмена в обработчике
                    #0000                                                       ; ResumeAddress, адрес продолжения генерируемой цепочки после HALT
                }
                assert $ == #6196
                endmodule
