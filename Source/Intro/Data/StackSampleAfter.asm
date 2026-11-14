                module IntroStackSampleAfter
                ; Документация [копия снимка SP в текстуре](../../../Docs/IntroStationTransition.md#снимок-стека-в-выборке-текстуры)
                assert $ == #65B6
                ; -----------------------------------------
                ; исходная физическая запись Initial
Initial:        FIntroStackSampleByte {
                    #00                                                         ; Value, исходный байт рядом со снимком SP, копируется при выборке текстуры
                }
                assert $ == #65B7
                endmodule
