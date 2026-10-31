                module PreviewContourSize
                ; Документация [контур и шаблоны заливки](../../../Docs/PreviewPolygonFill.md)
                assert $ == #C22B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewContourSize {
                    #00                                                         ; ByteCount, число байтов пар колонка и строка, рабочий профиль ненулевое чётное значение
                }
                assert $ == #C22C
                endmodule
