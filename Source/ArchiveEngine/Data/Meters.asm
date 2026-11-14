                module ArchiveEngineMeters
                ; Документация [экранные индикаторы](../../../Docs/ArchiveEngineMeters.md)
Value:          FArchiveEngineMeters {
                    #00,                                                        ; LeftTarget, заполняется при старте сцены
                    #00,                                                        ; RightTarget, заполняется при старте сцены
                    #00,                                                        ; LeftShown, сначала столбцов нет
                    #00,                                                        ; RightShown, сначала столбцов нет
                    #C040,                                                      ; LeftCursor, первый байт левой полосы
                    #C05F,                                                      ; RightCursor, последний байт правой полосы
                    #80,                                                        ; LeftMask, крайний левый бит байта
                    #01                                                         ; RightMask, крайний правый бит байта
                }
                endmodule
