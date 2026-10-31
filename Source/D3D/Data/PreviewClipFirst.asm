                module PreviewClipFirst
                ; Документация [концы и состояние отсечения](../../../Docs/PreviewClipSegment.md)
                assert $ == #C22C
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewProjectedVertex {
                    #0000,                                                      ; SecondAxis, знаковая колонка, первое физическое слово точки
                    #0000,                                                      ; FirstAxis, знаковая строка, второе физическое слово точки
                    #00                                                         ; Outcode, прямая младшая и инверсная старшая тетрада кода сторон
                }
                assert $ == #C231
                endmodule
