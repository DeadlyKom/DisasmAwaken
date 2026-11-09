                module PreviewObjectEnd
                ; Документация [подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)
                assert $ == #CE00
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewObjectEnd {
                    #80,                                                        ; Low, бит 7 завершает обход при старшем байте 80
                    #80                                                         ; High, 80 выбирает проверку специального маркера
                }
                assert $ == #CE02
                endmodule
