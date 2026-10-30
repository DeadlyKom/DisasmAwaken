                module MapClipWork
; Документация [рабочие точки и произведения](../../../Docs/ClipProducts.md)
                assert $ == #DE6B
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
TopProduct:     FClipProduct { #0000, #0000 }
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
BottomProduct:  FClipProduct { #0000, #0000 }
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
LeftProduct:    FClipProduct { #0000, #0000 }
                ; исходные нулевые поля, заполнение вычисляется во время исполнения
RightProduct:   FClipProduct { #0000, #0000 }
                assert $ == #DE7B
                endmodule
