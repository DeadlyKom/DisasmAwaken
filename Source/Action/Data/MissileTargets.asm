                module ActionMissileTargets
                ; Документация [проверка перед пуском ракет](../../../Docs/ActionMissileLaunch.md)
                assert $ == #9B1B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FMissileTargets {
                    #FF,                                                        ; Target0, код записи цели в слоте 0, FF означает отсутствие захвата
                    #FF,                                                        ; Target1, код записи цели в слоте 1, FF означает отсутствие захвата
                    #FF                                                         ; Target2, код записи цели в слоте 2, FF означает отсутствие захвата
                }
                assert $ == #9B1E
                endmodule
