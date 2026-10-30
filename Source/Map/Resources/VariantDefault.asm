                module MapVariantSprites
                module Default
; Документация [трёхстрочные фазы варианта](../../../Docs/AnimatedVariants.md)
                assert $ == #CD03
                ; Row0..Row2 содержат по два смежных экранных байта, сдвиг фазы соответствует младшим трём битам X
Phase0:         FMapVariantPhase { #00, #00, #40, #00, #00, #00 }
Phase1:         FMapVariantPhase { #00, #00, #20, #00, #00, #00 }
Phase2:         FMapVariantPhase { #00, #00, #10, #00, #00, #00 }
Phase3:         FMapVariantPhase { #00, #00, #08, #00, #00, #00 }
Phase4:         FMapVariantPhase { #00, #00, #04, #00, #00, #00 }
Phase5:         FMapVariantPhase { #00, #00, #02, #00, #00, #00 }
Phase6:         FMapVariantPhase { #00, #00, #01, #00, #00, #00 }
Phase7:         FMapVariantPhase { #00, #00, #00, #80, #00, #00 }
                assert $ == #CD33
                endmodule
                endmodule
