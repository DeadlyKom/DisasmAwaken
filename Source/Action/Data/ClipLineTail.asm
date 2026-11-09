                module ActionClipLineTail
                ; Документация [рабочие слова текущего отсечения](../../../Docs/ActionClippedLineWorkData.md)
                assert $ == #8D4A
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FClipLineTail {
                    #0000,                                                      ; NextFirst, полная вертикальная компонента следующей точки ломаной
                    #00,                                                        ; CurrentCode, полный ClipCode первой точки, ноль означает локальный отказ подготовки
                    #00                                                         ; NextCode, полный ClipCode следующей точки, ноль означает локальный отказ подготовки
                }
                assert $ == #8D4E
                endmodule
