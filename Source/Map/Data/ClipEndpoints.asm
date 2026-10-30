                module MapClipWork
; Документация [рабочие точки и произведения](../../../Docs/ClipProducts.md)
                assert $ == #DE2F
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
FirstPoint:     FProjectedPoint { #0000, #0000, #00 }
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
SecondPoint:    FProjectedPoint { #0000, #0000, #00 }
                assert $ == #DE39
                endmodule
