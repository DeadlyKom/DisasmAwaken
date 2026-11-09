                module ActionOtherContext
                ; Документация [локальные поля контекста](../../../Docs/ActionLocalContextPhysicalData.md)
                assert $ == #9BC6
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FContextWordPair {
                    #4B38,                                                      ; OtherFirst, первое слово для сравнения с SeedFirst
                    #4AF4                                                       ; OtherSecond, второе слово для сравнения с SeedSecond
                }
                assert $ == #9BCA
                endmodule
