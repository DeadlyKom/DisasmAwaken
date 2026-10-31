                module PreviewLineTail
                ; Документация [разнесённое состояние полилинии](../../../Docs/PreviewClippedFaceStream.md)
                assert $ == #C26B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewLineTail {
                    #0000,                                                      ; CurrentRow, слово строки очередного конца полилинии
                    #00,                                                        ; PreviousCode, полный код сторон предыдущего конца
                    #00                                                         ; CurrentCode, полный код сторон очередного конца
                }
                assert $ == #C26F
                endmodule
