                module MapChainWork
; Документация [открытая цепочка карты](../../../Docs/MapPointChain.md)
                assert $ == #DE1B
                ; исходные X,Y и ClipCodes, все пять байтов обновляются перед обработкой ребра
PreviousPoint:  FProjectedPoint { #0000, #0000, #00 }
                assert $ == #DE20
                endmodule
