                module ArchiveEngineScene
                ; Документация [шаг и область вывода](../../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; Документация [границы проверки оставшихся полей](../../../Docs/Scene1PixelPairs.md#оставшиеся-поля-записи-сцены)
View:           FArchiveEngineScene {
                    #005C,                                                      ; RowBytes, 92 байта
                    #005A,                                                      ; SourceWidth, 90 байтов
                    #003A,                                                      ; MaxHorizontal, 58 байтов
                    #00CB,                                                      ; SourceRows, 203 строки
                    #000B,                                                      ; MaxVertical, 11 строк
                    #00,                                                        ; VerticalOffset
                    #00,                                                        ; Unknown0B
                    #A100,                                                      ; ViewColumn, инициализация заменяет на #771D
                    #0B,                                                        ; SpriteYBias, 11 строк
                    #0000                                                       ; MeterGapSource, заполняется перед выводом середины кадра
                }
                endmodule
