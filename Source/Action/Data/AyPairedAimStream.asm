                module ActionAyStreams
                ; Документация [строки звуковых потоков](../../../Docs/ActionAyStreams.md)
                assert $ == #EE34
PairedAimRow00: FActionAyFrame {
                    #10,                                                        ; ToneLow, младший байт периода
                    #01,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #0C                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimRow01: FActionAyFrame {
                    #40,                                                        ; ToneLow, младший байт периода
                    #01,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #0B                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimRow02: FActionAyFrame {
                    #70,                                                        ; ToneLow, младший байт периода
                    #01,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #0A                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimRow03: FActionAyFrame {
                    #20,                                                        ; ToneLow, младший байт периода
                    #02,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #09                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimRow04: FActionAyFrame {
                    #E0,                                                        ; ToneLow, младший байт периода
                    #02,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #08                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimRow05: FActionAyFrame {
                    #20,                                                        ; ToneLow, младший байт периода
                    #03,                                                        ; ToneHigh, старший байт периода, полный исходный байт
                    #08,                                                        ; MixerBits, байт для OR со смесителем, B предварительно выполняет RLCA
                    #07                                                         ; Volume, байт записи уровня, полный исходный байт
                }
PairedAimEnd:   db #00                                                          ; нулевой ToneLow следующей строки, отключить поток
                assert $ == #EE4D
                endmodule
