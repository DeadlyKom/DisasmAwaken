                module Save4NewsTransfer
                ; Документация [перенос тела NEWS](../../../Docs/StationNewsTransfer.md)
                assert $ == #0085
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FStationNewsTransfer {
                    #00,                                                        ; EndHour, при переносе занимает байт часа окончания из авторского NEWS
                    #0000,                                                      ; SystemWord0, при переносе занимает первое слово системы в NEWS
                    #0000,                                                      ; SystemWord1, при переносе занимает второе слово системы в NEWS
                    #01                                                         ; PlanetIndex, при переносе занимает номер планеты в NEWS
                }
                assert $ == #008B
                endmodule
