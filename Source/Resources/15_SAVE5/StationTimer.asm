                module Save5StationTimer
                ; Документация [состояние дискового слота](../../../Docs/SavedStateLayout.md)
                ; Смещения относятся к файлу, перенос в 983B выполняют исходные обработчики.
                assert $ == #0000
Counter:        FStationBcdCounter {
                    #00,                                                        ; FStationBcdCounter.MidHigh, значение дискового слота
                    #00,                                                        ; FStationBcdCounter.High, значение дискового слота
                    #00,                                                        ; FStationBcdCounter.MidLow, значение дискового слота
                    #00                                                         ; FStationBcdCounter.Low, значение дискового слота
                }
                assert $ == #0004
                endmodule
