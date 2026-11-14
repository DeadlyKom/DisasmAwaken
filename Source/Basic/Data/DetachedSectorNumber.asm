                module BasicDetachedNumber
                ; Документация [число за логическим BASIC](../../../Docs/BasicProgram.md)
                assert $ == #0084
Digits:         db "15616", #0E                                                 ; печатное представление числа и маркер двоичного значения
Value:          FBasicSmallInteger { #00, #00, #00, #3D, #00 }                  ; положительное целое #3D00
EndByte:        db #0D                                                          ; исходный CR после числа
                assert $ == #0090
                endmodule
