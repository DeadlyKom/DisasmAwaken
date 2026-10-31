                module PreviewLineCoordinates
                ; Документация [разнесённое состояние полилинии](../../../Docs/PreviewClippedFaceStream.md)
                assert $ == #C25B
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewLineCoordinates {
                    #0000,                                                      ; PreviousColumn, слово колонки предыдущего конца полилинии
                    #0000,                                                      ; PreviousRow, слово строки предыдущего конца полилинии
                    #0000                                                       ; CurrentColumn, слово колонки очередного конца полилинии
                }
                assert $ == #C261
                endmodule
