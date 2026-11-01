                module MusicRowCounters
                ; Документация [физические данные проигрывателя](../../../Docs/MusicPlayerData.md)
                assert $ == #DE1E
                ; -----------------------------------------
                ; исходная физическая запись ChannelA
ChannelA:       FMusicRowCounter {
                    #00                                                         ; Remaining, байтовая длительность строки, DEC исходного нуля даёт FF
                }
                assert $ == #DE1F
                endmodule
