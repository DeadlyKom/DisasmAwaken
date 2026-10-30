                module MapVariantSprites
                module Selected
; Документация [трёхстрочные фазы варианта](../../../Docs/AnimatedVariants.md)
                assert $ == #CD93
                ; Row0..Row2 содержат по два смежных экранных байта, сдвиг фазы соответствует младшим трём битам X
Phase0:         FMapVariantPhase { #40, #00, #E0, #00, #40, #00 }
Phase1:         FMapVariantPhase { #20, #00, #70, #00, #20, #00 }
Phase2:         FMapVariantPhase { #10, #00, #38, #00, #10, #00 }
Phase3:         FMapVariantPhase { #08, #00, #1C, #00, #08, #00 }
Phase4:         FMapVariantPhase { #04, #00, #0E, #00, #04, #00 }
Phase5:         FMapVariantPhase { #02, #00, #07, #00, #02, #00 }
Phase6:         FMapVariantPhase { #01, #00, #03, #80, #01, #00 }
Phase7:         FMapVariantPhase { #00, #80, #01, #C0, #00, #80 }
                assert $ == #CDC3
                endmodule
                endmodule
