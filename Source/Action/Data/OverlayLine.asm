                module ActionOverlayLineData
                ; Документация [физические данные связанного состояния](../../../Docs/ActionOverlayPair.md)
                assert $ == #EB6E
                ; -----------------------------------------
                ; исходная физическая запись Line
Line:           FOverlayLine {
                    #B2,                                                        ; Header, B2, открытый XOR-сегмент из двух вершин
                    #00,                                                        ; FirstIndex, байтовое смещение первой FRenderProjectedPoint
                    #05,                                                        ; SecondIndex, байтовое смещение второй FRenderProjectedPoint
                    #00                                                         ; Terminator, полный нулевой конец потока
                }
                assert $ == #EB72
                endmodule
