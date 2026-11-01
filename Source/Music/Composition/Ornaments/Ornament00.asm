                module AntichristOrnament00
                ; Документация [исходная композиция](../../../../Docs/MusicComposition.md)
                assert $ == #F6D4
                ; -----------------------------------------
                ; исходная физическая запись Header
Header:         FMusicLoopHeader {
                    #00,                                                        ; LoopPosition, позиция возврата после достижения длины
                    #01                                                         ; Length, число физических шагов
                }
                ; -----------------------------------------
                ; исходная физическая запись Step00
Step00:         FMusicOrnamentStep {
                    #00                                                         ; NoteDelta, байтовая поправка индекса ноты с оборачиванием при сложении
                }
                assert $ == #F6D7
                endmodule
