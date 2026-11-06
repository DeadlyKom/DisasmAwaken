                module ActionWorkVector
                ; Документация [вычитание рабочего вектора](../../../Docs/ActionSubtractWorkVector.md)
                assert $ == #9B78
Value:          FActionWorkVector24 {
                    {                                                           ; Component0, исходная физическая компонента
                        #0000,                                                  ; LowWord, исходные разряды 15..0
                        #00                                                     ; High, исходные разряды 23..16 со знаком в бите 7
                    },
                    {                                                           ; Component1, исходная физическая компонента
                        #0000,                                                  ; LowWord, исходные разряды 15..0
                        #00                                                     ; High, исходные разряды 23..16 со знаком в бите 7
                    },
                    {                                                           ; Component2, исходная физическая компонента
                        #F7FF,                                                  ; LowWord, исходные разряды 15..0
                        #FF                                                     ; High, исходные разряды 23..16 со знаком в бите 7
                    }
                }
                assert $ == #9B81
                endmodule
