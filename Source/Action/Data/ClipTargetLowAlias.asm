                module ActionClipTargetLowAlias
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF08
                ; -----------------------------------------
                ; исходная физическая запись Row0Tail
Row0Tail:       FClipTargetLowAlias {
                    LOW(@Action.ClipInsideToTop.Entry),                         ; SecondSides8, младший байт @Action.ClipInsideToTop.Entry, индекс 08
                    LOW(@Action.ClipInsideToTopRight.Entry),                    ; SecondSides9, младший байт @Action.ClipInsideToTopRight.Entry, индекс 09
                    LOW(@Action.ClipInsideToTopLeft.Entry)                      ; SecondSidesA, младший байт @Action.ClipInsideToTopLeft.Entry, индекс 0A
                }
                assert $ == #CF0B
                endmodule
