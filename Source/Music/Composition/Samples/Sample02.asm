                module AntichristSample02
                ; Документация [исходная композиция](../../../../Docs/MusicComposition.md)
                assert $ == #F5BA
                ; -----------------------------------------
                ; исходная физическая запись Header
Header:         FMusicLoopHeader {
                    #00,                                                        ; LoopPosition, позиция возврата после достижения длины
                    #01                                                         ; Length, число физических шагов
                }
                ; -----------------------------------------
                ; исходная физическая запись Step00
Step00:         FMusicSampleStep {
                    #01,                                                        ; ShiftControl, управление уровнем и шумовым либо огибающим вкладом
                    #0E,                                                        ; LevelModes, базовый уровень, накопление и вклад в микшер
                    #0000                                                       ; ToneDelta, слово тональной поправки
                }
                assert $ == #F5C0
                endmodule
