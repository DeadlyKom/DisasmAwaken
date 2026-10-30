                module StationIrqData
; Документация [StationInterrupt](../../../Docs/StationInterrupt.md)
                assert $ == #9C13
Storage:        FStationIrqStorage {
                    #0000,                                                      ; FStationIrqStorage.Scratch00
                    #0000,                                                      ; FStationIrqStorage.Scratch01
                    #0000,                                                      ; FStationIrqStorage.Scratch02
                    #0000,                                                      ; FStationIrqStorage.Scratch03
                    #0000,                                                      ; FStationIrqStorage.Scratch04
                    #0000,                                                      ; FStationIrqStorage.Scratch05
                    #0000,                                                      ; FStationIrqStorage.Scratch06
                    #0000,                                                      ; FStationIrqStorage.Scratch07
                    #0000,                                                      ; FStationIrqStorage.Scratch08
                    #0000,                                                      ; FStationIrqStorage.Scratch09
                    #0000,                                                      ; FStationIrqStorage.Scratch10
                    #0000,                                                      ; FStationIrqStorage.Scratch11
                    #0000,                                                      ; FStationIrqStorage.Scratch12
                    #0000,                                                      ; FStationIrqStorage.SavedPage
                    #0000,                                                      ; FStationIrqStorage.SavedBCAlt
                    #0000,                                                      ; FStationIrqStorage.SavedDEAlt
                    #0000,                                                      ; FStationIrqStorage.SavedHLAlt
                    #0000,                                                      ; FStationIrqStorage.SavedAFAlt
                    #0000,                                                      ; FStationIrqStorage.SavedBC
                    #0000,                                                      ; FStationIrqStorage.SavedDE
                    #0000,                                                      ; FStationIrqStorage.SavedHL
                    #0000,                                                      ; FStationIrqStorage.SavedAF
                    #0000,                                                      ; FStationIrqStorage.SavedIY
                    #0000                                                       ; FStationIrqStorage.SavedIX
                }
StackTop:       assert $ == #9C43
                endmodule
