                module ActionContextIndex
                ; Документация [локальные поля контекста](../../../Docs/ActionLocalContextPhysicalData.md)
                assert $ == #9BCA
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FContextPublishIndex {
                    #02                                                         ; SelectedIndex, байт публикации при совпадении обеих пар контекста
                }
                assert $ == #9BCB
                endmodule
