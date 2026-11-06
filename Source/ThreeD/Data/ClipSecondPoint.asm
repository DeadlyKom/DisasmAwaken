                module ThreeDClipPoints
                ; Документация [точки и пересечения](../../../Docs/ThreeDOverlayMirror.md)
                assert $ == #CF1B
SecondPoint:    FRenderProjectedPoint {
                    #0000,                                                      ; Second, исходная горизонтальная координата
                    #0000,                                                      ; First, исходная вертикальная координата
                    #00                                                         ; ClipCode, исходный нуль означает ещё не подготовленный код
                }
                assert $ == #CF20
                endmodule
