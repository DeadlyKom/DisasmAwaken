                module ArchiveEngine
                module ReuseFrameIndex
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; перенос номера текущего шага в начальный индекс новой группы
                ; In:
                ;   IX - запись бойца
                ; Out:
                ;   BC - B, прежний индекс шага, C сохранён
                ; Corrupt:
                ;   BC
                ; -----------------------------------------
Entry:          LD B, (IX + @FArchiveEngineFighter.StepIndex)
                RET

                endmodule
                endmodule
