                module ThreeDClipPoints
                ; Документация [точки и пересечения](../../../Docs/ThreeDOverlayMirror.md)
                assert $ == #CF0B
FirstPoint:     FRenderProjectedPoint {
                    #0000,                                                      ; Second, исходная горизонтальная координата
                    #0000,                                                      ; First, исходная вертикальная координата
                    #00                                                         ; ClipCode, исходный нуль означает ещё не подготовленный код
                }
                assert $ == #CF10
                endmodule
