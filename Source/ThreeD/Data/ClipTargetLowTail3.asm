                module ThreeDClipTargetLowTail3
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF3B
                ; -----------------------------------------
                ; исходная физическая запись First3Tail
First3Tail:     FClipTargetLowTail {
                    #00,                                                        ; SecondSidesB, индекс 3B вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesC, индекс 3C вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesD, индекс 3D вне 81 нормальной пары, исходный байт сохранён
                    #00,                                                        ; SecondSidesE, индекс 3E вне 81 нормальной пары, исходный байт сохранён
                    #00                                                         ; SecondSidesF, индекс 3F вне 81 нормальной пары, исходный байт сохранён
                }
                assert $ == #CF40
                endmodule
