                module MapVariantSprites
                module Current
; Документация [трёхстрочные фазы варианта](../../../Docs/AnimatedVariants.md)
                assert $ == #CD33
                ; Row0..Row2 содержат по два смежных экранных байта, сдвиг фазы соответствует младшим трём битам X
Phase0:         FMapVariantPhase { #A0, #00, #40, #00, #A0, #00 }
Phase1:         FMapVariantPhase { #50, #00, #20, #00, #50, #00 }
Phase2:         FMapVariantPhase { #28, #00, #10, #00, #28, #00 }
Phase3:         FMapVariantPhase { #14, #00, #08, #00, #14, #00 }
Phase4:         FMapVariantPhase { #0A, #00, #04, #00, #0A, #00 }
Phase5:         FMapVariantPhase { #05, #00, #02, #00, #05, #00 }
Phase6:         FMapVariantPhase { #02, #80, #01, #00, #02, #80 }
Phase7:         FMapVariantPhase { #01, #40, #00, #80, #01, #40 }
                assert $ == #CD63
                endmodule
                endmodule
