                module ActionFlightCounter
                ; Документация [физическое состояние панели](../../../Docs/ActionPanelPhysicalData.md)
                assert $ == #9BBD
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FFlightBcdCounter {
                    #22,                                                        ; MidHigh, BCD-пара разрядов 10^4 и 10^5, регистр E
                    #01,                                                        ; High, BCD-пара разрядов 10^6 и 10^7, регистр D
                    #10,                                                        ; Low, BCD-пара разрядов 10^0 и 10^1, регистр L
                    #10                                                         ; MidLow, BCD-пара разрядов 10^2 и 10^3, регистр H
                }
                assert $ == #9BC1
                endmodule
