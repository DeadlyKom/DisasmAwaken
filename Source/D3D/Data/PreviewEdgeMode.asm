                module PreviewEdgeMode
                ; Документация [физические параметры ребра](../../../Docs/PreviewEdgeRaster.md)
                assert $ == #C26F
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewEdgeMode {
                    #00,                                                        ; PixelOpcode, байт пиксельной инструкции A1 для AND, A9 для XOR, B1 для OR
                    #00                                                         ; BoundaryOpcode, байт перехода 30 для JR NC при AND, 38 для JR C при XOR и OR
                }
                assert $ == #C271
                endmodule
