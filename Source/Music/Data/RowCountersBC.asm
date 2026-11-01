                module MusicRowCounters
                ; Документация [физические данные проигрывателя](../../../Docs/MusicPlayerData.md)
                assert $ == #DC0E
                ; -----------------------------------------
                ; исходная физическая запись ChannelB
ChannelB:       FMusicRowCounter {
                    #00                                                         ; Remaining, байтовая длительность строки, DEC исходного нуля даёт FF
                }
                ; -----------------------------------------
                ; исходная физическая запись ChannelC
ChannelC:       FMusicRowCounter {
                    #00                                                         ; Remaining, байтовая длительность строки, DEC исходного нуля даёт FF
                }
                assert $ == #DC10
                endmodule
