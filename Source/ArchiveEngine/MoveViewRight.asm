                module ArchiveEngine
                module MoveViewRight
                ; Документация [границы окна](../../Docs/FighterAssets.md#горизонтальные-границы-сцены)
                ; -----------------------------------------
                ; сдвиг начала окна на один байт вправо до правого предела
                ; In:
                ;   младший байт ViewColumn содержит горизонтальное смещение
                ; Out:
                ;   при смещении меньше MaxHorizontal младший байт увеличен, старший сохранён
                ; Corrupt:
                ;   HL, AF
                ; -----------------------------------------
                ; проверка правой границы по младшим байтам полей
Entry:          LD A, (@ArchiveEngineScene.View.ViewColumn)
                LD HL, @ArchiveEngineScene.View.MaxHorizontal
                CP (HL)
                RET NC                                                          ; выход, если окно достигло правой границы или вышло за неё

                INC A
                LD (@ArchiveEngineScene.View.ViewColumn), A
                RET

                endmodule
                endmodule
