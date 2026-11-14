                module ActionPanelSignedWord
                ; Документация [физическое состояние панели](../../../Docs/ActionPanelPhysicalData.md)
                assert $ == #A78F
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPanelSignedWord {
                    #0014                                                       ; Value, знаковая скорость для вектора движения и шестой шкалы
                }
                assert $ == #A791
                endmodule
