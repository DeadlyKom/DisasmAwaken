                module AntichristHeader
                ; Документация [исходная композиция](../../../Docs/MusicComposition.md)
                ; Поле ToneTableIndex [доказательство по периодам](../../../Docs/MusicToneTableIndex.md)
                assert $ == #E700
                ; -----------------------------------------
                ; исходная физическая запись Entry
Entry:          FMusicModuleHeader {
                ; Description, 99 исходных символов названия, автора и строки компилятора
                    { "ProTracker 3.6 compilation of            Antichrist            by SET/ELLiPSE GROUP     01.11.2000 " },
                    #02,                                                        ; ToneTableIndex, номер частотной таблицы PT3, 2 соответствует ASM/PSC, InitializeModule его пропускает
                    #03,                                                        ; RowTempo, начальное количество тиков на строку, копируется в изменяемый операнд
                    #1C,                                                        ; PositionCount, байт количества позиций, попадает в F при POP AF, границу списка задаёт FF
                    #04,                                                        ; LoopIndex, смещение позиции возврата от начала списка в байтах
                    #00E6                                                       ; PatternTable, относительный адрес таблицы троек указателей
                }
                assert $ == #E769
                endmodule
