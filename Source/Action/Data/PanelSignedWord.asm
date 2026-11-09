                module ActionPanelSignedWord
                ; Документация [физическое состояние панели](../../../Docs/ActionPanelPhysicalData.md)
                assert $ == #A78F
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPanelSignedWord {
                    #0014                                                       ; Value, знаковое слово источника шестой шкалы, полный игровой смысл и единицы неизвестны
                }
                assert $ == #A791
                endmodule
