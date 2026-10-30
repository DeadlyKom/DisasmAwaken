                module MapClipWork
; Документация [состояние углов](../../../Docs/ClipCases.md)
                assert $ == #DE39
                ; исходные SeenFlags=0, BlockCode=0, это дисковый снимок до вызовов
Corners:        FClipCornerState { #00, #00 }
                assert $ == #DE3B
                endmodule
