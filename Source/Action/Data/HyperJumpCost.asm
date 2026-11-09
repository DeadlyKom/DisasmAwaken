                module ActionHyperJumpCost
                ; Документация [исходные записи и стоимость гиперперехода](../../../Docs/ActionNewsOrdersAndJumpCost.md)
                assert $ == #9C8A
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FHyperJumpCost {
                    #00                                                         ; Cost, базовая стоимость гиперперехода, маршрут Preferred удваивает её в слове
                }
                assert $ == #9C8B
                endmodule
