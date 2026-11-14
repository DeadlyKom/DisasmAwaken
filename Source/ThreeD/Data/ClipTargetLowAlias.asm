                module ThreeDClipTargetLowAlias
                ; Документация [физические младшие байты диспетчера](../../../Docs/ClipTargetLowPhysicalData.md)
                assert $ == #CF08
                ; -----------------------------------------
                ; исходная физическая запись Row0Tail
Row0Tail:       FClipTargetLowAlias {
                    LOW(@ThreeD.ClipInsideToTop.Entry),                         ; SecondSides8, младший байт @ThreeD.ClipInsideToTop.Entry, индекс 08
                    LOW(@ThreeD.ClipInsideToTopRight.Entry),                    ; SecondSides9, младший байт @ThreeD.ClipInsideToTopRight.Entry, индекс 09
                    LOW(@ThreeD.ClipInsideToTopLeft.Entry)                      ; SecondSidesA, младший байт @ThreeD.ClipInsideToTopLeft.Entry, индекс 0A
                }
                assert $ == #CF0B
                endmodule
