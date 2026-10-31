                module PreviewObjectAngles
                ; Документация [параметры обхода очереди](../../../Docs/PreviewQueueRender.md)
                assert $ == #C21E
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewObjectAngles {
                    #00,                                                        ; First, первый байтовый параметр ориентации объекта
                    #00,                                                        ; Second, второй байтовый параметр ориентации объекта
                    #00                                                         ; Third, третий байтовый параметр ориентации объекта
                }
                assert $ == #C221
                endmodule
