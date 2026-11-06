                module ActionTransformWorkVector
                ; Документация [рабочий вектор](../../../Docs/ActionPrepareBodyTransform.md)
                assert $ == #9B6F
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
                        #8000,                                                  ; LowWord, исходные разряды 15..0
                        #E0                                                     ; High, исходные разряды 23..16 со знаком в бите 7
                    }
                }
                assert $ == #9B78
                endmodule
