                module Save0StationTimer
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0000
Counter:        FStationBcdCounter {
                    #22,                                                        ; FStationBcdCounter.MidHigh, значение дискового слота
                    #01,                                                        ; FStationBcdCounter.High, значение дискового слота
                    #10,                                                        ; FStationBcdCounter.MidLow, значение дискового слота
                    #15                                                         ; FStationBcdCounter.Low, значение дискового слота
                }
                assert $ == #0004
                endmodule
