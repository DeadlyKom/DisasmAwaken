                module PreviewFillMode
                ; Документация [контур и шаблоны заливки](../../../Docs/PreviewPolygonFill.md)
                assert $ == #C23B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewFillMode {
                    #00                                                         ; Index, индекс пары внутренних шаблонов, крайние маски доказаны только для 0..4
                }
                assert $ == #C23C
                endmodule
