                module StationTimer
; Документация [StationInterrupt](../../../Docs/StationInterrupt.md)
                assert $ == #983B
Counter:        FStationBcdCounter {
                    #22,                                                        ; FStationBcdCounter.MidHigh
                    #01,                                                        ; FStationBcdCounter.High
                    #10,                                                        ; FStationBcdCounter.MidLow
                    #10                                                         ; FStationBcdCounter.Low
                }
                endmodule
