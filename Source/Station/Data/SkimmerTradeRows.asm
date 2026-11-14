                module StationSkimmerTradeRows
                ; Документация [физические записи транспорта и количества](../../../Docs/StationTransportTradeTables.md)
                assert $ == #9825
                ; -----------------------------------------
                ; исходная физическая запись Skimmer0
Skimmer0:       FStationSkimmerTradeRow {
                    #00,                                                        ; Unknown00, тоннаж из CNSK, Entry читателя Capacity при индексах 7..10 читает это поле, штатная роль не установлена
                    #7530,                                                      ; PriceField, слово свойства c второго набора, сценарий покупки отсутствует
                    #AA,                                                        ; Unknown03, скорость из CNSK, текущий потребитель и единицы не установлены
                    #05                                                         ; LoadAddend, свойство v и добавка в ComputeWeightedLoad
                }
                ; -----------------------------------------
                ; исходная физическая запись Skimmer1
Skimmer1:       FStationSkimmerTradeRow {
                    #00,                                                        ; Unknown00, тоннаж из CNSK, Entry читателя Capacity при индексах 7..10 читает это поле, штатная роль не установлена
                    #6978,                                                      ; PriceField, слово свойства c второго набора, сценарий покупки отсутствует
                    #96,                                                        ; Unknown03, скорость из CNSK, текущий потребитель и единицы не установлены
                    #04                                                         ; LoadAddend, свойство v и добавка в ComputeWeightedLoad
                }
                ; -----------------------------------------
                ; исходная физическая запись Skimmer2
Skimmer2:       FStationSkimmerTradeRow {
                    #00,                                                        ; Unknown00, тоннаж из CNSK, Entry читателя Capacity при индексах 7..10 читает это поле, штатная роль не установлена
                    #5DC0,                                                      ; PriceField, слово свойства c второго набора, сценарий покупки отсутствует
                    #82,                                                        ; Unknown03, скорость из CNSK, текущий потребитель и единицы не установлены
                    #03                                                         ; LoadAddend, свойство v и добавка в ComputeWeightedLoad
                }
                ; -----------------------------------------
                ; исходная физическая запись Skimmer3
Skimmer3:       FStationSkimmerTradeRow {
                    #00,                                                        ; Unknown00, тоннаж из CNSK, Entry читателя Capacity при индексах 7..10 читает это поле, штатная роль не установлена
                    #4650,                                                      ; PriceField, слово свойства c второго набора, сценарий покупки отсутствует
                    #64,                                                        ; Unknown03, скорость из CNSK, текущий потребитель и единицы не установлены
                    #02                                                         ; LoadAddend, свойство v и добавка в ComputeWeightedLoad
                }
                assert $ == #9839
                endmodule
