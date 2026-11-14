                module ActionArchivedSpawnChances
                ; Документация [авторский хвост параметров и WERPO](../../../Docs/ActionQueueParameterPhysicalData.md)
                assert $ == #9BB3
ParameterTail:  db #00                                                          ; последний байт авторского PLANDICTAT, отдельное назначение неизвестно
Value:          FArchivedSpawnChances {
                    #00,                                                        ; Pirates, пираты
                    #00,                                                        ; Civilians, мирные корабли
                    #00,                                                        ; Police, полиция
                    #00,                                                        ; Military, военные
                    #00,                                                        ; Legion, легионеры
                    #00,                                                        ; SecondPirates, вторая группа пиратов
                    #00,                                                        ; Ufo, НЛО
                    #00,                                                        ; SecondUfo, вторая группа НЛО
                    #00                                                         ; Hermit, отшельник
                }
                assert $ == #9BBD
                endmodule
