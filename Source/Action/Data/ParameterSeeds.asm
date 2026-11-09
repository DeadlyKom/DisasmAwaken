                module ActionParameterSeeds
                ; Документация [физические входные состояния](../../../Docs/ActionInputContextData.md)
                assert $ == #9BC1
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FParameterSeeds {
                    #4B38,                                                      ; SeedFirst, первое слово исходного зерна
                    #4AF4,                                                      ; SeedSecond, второе слово исходного зерна
                    #00                                                         ; StepControl, полный управляющий байт повторов генератора
                }
                assert $ == #9BC6
                endmodule
