                module ActionMissileStockState
                ; Документация [выбор остатка ракет](../../../Docs/ActionMissileStock.md)
                assert $ == #9C12
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FMissileStock {
                    #64,                                                        ; Fallback, запас ракет рп1 из строки 2 станции, выбирается при нулевом Preferred
                    #00                                                         ; Preferred, запас ракет рп2 из строки 3 станции, выбирается первым при ненулевом значении
                }
                assert $ == #9C14
                endmodule
