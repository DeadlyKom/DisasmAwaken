                module MapVariantSprites
                module Stored
; Документация [трёхстрочные фазы варианта](../../../Docs/AnimatedVariants.md)
                assert $ == #CD63
                ; Row0..Row2 содержат по два смежных экранных байта, сдвиг фазы соответствует младшим трём битам X
Phase0:         FMapVariantPhase { #E0, #00, #A0, #00, #E0, #00 }
Phase1:         FMapVariantPhase { #70, #00, #50, #00, #70, #00 }
Phase2:         FMapVariantPhase { #38, #00, #28, #00, #38, #00 }
Phase3:         FMapVariantPhase { #1C, #00, #14, #00, #1C, #00 }
Phase4:         FMapVariantPhase { #0E, #00, #0A, #00, #0E, #00 }
Phase5:         FMapVariantPhase { #07, #00, #05, #00, #07, #00 }
Phase6:         FMapVariantPhase { #03, #80, #02, #80, #03, #80 }
Phase7:         FMapVariantPhase { #01, #C0, #01, #40, #01, #C0 }
                assert $ == #CD93
                endmodule
                endmodule
