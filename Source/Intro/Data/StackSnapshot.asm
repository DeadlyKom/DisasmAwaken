                module IntroStackSnapshot
                ; Документация [передача управления станции](../../../Docs/IntroStationTransition.md)
                assert $ == #65B4
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FIntroStackSnapshot {
                    #0000                                                       ; Stack, слово SP после подготовки экрана и до смены банка
                }
                assert $ == #65B6
                endmodule
