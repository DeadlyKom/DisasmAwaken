                module MapChainWork
; Документация [открытая цепочка карты](../../../Docs/MapPointChain.md)
                assert $ == #DE0B
                ; исходные X,Y и ClipCodes, все пять байтов обновляются перед обработкой ребра
CurrentPoint:   FProjectedPoint { #0000, #0000, #00 }
                assert $ == #DE10
                endmodule
