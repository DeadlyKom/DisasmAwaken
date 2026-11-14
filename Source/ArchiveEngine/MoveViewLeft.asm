                module ArchiveEngine
                module MoveViewLeft
                ; Документация [границы окна](../../Docs/FighterAssets.md#горизонтальные-границы-сцены)
                ; -----------------------------------------
                ; сдвиг начала окна на один байт влево до нулевого смещения
                ; In:
                ;   младший байт ViewColumn содержит горизонтальное смещение
                ; Out:
                ;   ненулевой младший байт уменьшен, старший сохранён
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
                ; проверка левой границы перед уменьшением смещения
Entry:          LD A, (@ArchiveEngineScene.View.ViewColumn)
                OR A
                RET Z                                                           ; выход, если окно уже у левой границы

                DEC A
                LD (@ArchiveEngineScene.View.ViewColumn), A
                RET

                endmodule
                endmodule
