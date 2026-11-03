                module ActionMissileStockState
                ; Документация [выбор остатка ракет](../../../Docs/ActionMissileStock.md)
                assert $ == #9C12
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FMissileStock {
                    #64,                                                        ; Fallback, выбирается при нулевом Preferred, вид этого запаса пока не установлен
                    #00                                                         ; Preferred, выбирается первым при ненулевом значении, вид этого запаса пока не установлен
                }
                assert $ == #9C14
                endmodule
