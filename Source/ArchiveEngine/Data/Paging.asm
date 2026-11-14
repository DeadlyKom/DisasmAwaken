                module ArchiveEnginePages
                ; Документация [выбор страниц](../../../Docs/ArchiveEnginePaging.md)
State:          FArchiveEnginePagingState {
                    #00,                                                        ; CurrentCode, исходная страница
                    #00                                                         ; IrqSavedCode, заполняется при каждом IRQ
                }
SpriteCodes:    FArchiveEngineSpritePages {
                    #08,                                                        ; Bd0
                    #09,                                                        ; Bd1
                    #0A,                                                        ; Bd2
                    #0B                                                         ; Bd3
                }
Targets:        FArchiveEngineModeTargets {
                    @ArchiveEngine.SelectPentagonPage.Entry,                    ; Pentagon
                    @ArchiveEngine.SelectScorpionPage.Entry,                    ; Scorpion
                    @ArchiveEngine.SelectAtmPage.Entry                          ; Atm
                }
                endmodule
