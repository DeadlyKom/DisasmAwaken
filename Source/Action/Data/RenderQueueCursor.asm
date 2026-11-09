                module ActionRenderQueueCursor
                ; Документация [поля очереди и параметров](../../../Docs/ActionQueueParameterPhysicalData.md)
                assert $ == #9BA1
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FRenderQueueCursor {
                    #00,                                                        ; Head, младшее смещение головы в странице 8F, рабочий конец цепочки 01
                    #00                                                         ; FreeOffset, смещение следующего узла, рабочий шаг 0E и признак исчерпания FC
                }
                assert $ == #9BA3
                endmodule
