                module TexturePhases
; Документация [фазы вступления](../../../Docs/Intro.md)
; PhaseA управляет младшим байтом HL, PhaseB альтернативным BC, PhaseC альтернативным HL
                assert $ == #6C8A
PhaseA:         FTexturePhase {
                    #5080,                                                      ; FTexturePhase.Phase
                    #0000,                                                      ; FTexturePhase.Step
                    #0030                                                       ; FTexturePhase.StepDelta
                }
PhaseB:         FTexturePhase {
                    #4080,                                                      ; FTexturePhase.Phase
                    #0000,                                                      ; FTexturePhase.Step
                    #0018                                                       ; FTexturePhase.StepDelta
                }
PhaseC:         FTexturePhase {
                    #5880,                                                      ; FTexturePhase.Phase
                    #0000,                                                      ; FTexturePhase.Step
                    #0038                                                       ; FTexturePhase.StepDelta
                }
                assert $ == #6C9C
                endmodule
