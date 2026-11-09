                module ActionPanelEvents
                ; Документация [физическое состояние панели](../../../Docs/ActionPanelPhysicalData.md)
                assert $ == #A78C
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPanelEventFlags {
                    #00                                                         ; Flags, UpdateFrame использует биты 0, 1 и 2, остальные биты не интерпретируются
                }
                assert $ == #A78D
                endmodule
