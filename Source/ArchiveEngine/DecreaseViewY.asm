                module ArchiveEngine
                module DecreaseViewY
                ; Документация [границы окна](../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; -----------------------------------------
                ; уменьшение номера исходной строки начала окна до нуля
                ; In:
                ;   VerticalOffset содержит текущее смещение окна в строках
                ; Out:
                ;   ненулевое смещение уменьшено на единицу
                ; Corrupt:
                ;   AF
                ; Note:
                ;   штатный переход на этот вход не установлен
                ; -----------------------------------------
                ; проверка нулевого смещения перед уменьшением
Entry:          LD A, (@ArchiveEngineScene.View.VerticalOffset)
                OR A
                RET Z                                                           ; выход, если смещение равно нулю

                DEC A
                LD (@ArchiveEngineScene.View.VerticalOffset), A
                RET

                endmodule
                endmodule
