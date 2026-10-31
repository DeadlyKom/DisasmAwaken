                module PreviewEdgeEndpoints
                ; Документация [физические параметры ребра](../../../Docs/PreviewEdgeRaster.md)
                assert $ == #C24B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewEdgeEndpoints {
                    #0000,                                                      ; StartPoint, начальное слово, младший байт колонка, старший строка
                    #0000                                                       ; EndPoint, конечное слово в том же формате
                }
                assert $ == #C24F
                endmodule
