                module ArchiveEngine
                module FlipFighterSide
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; переключение младшего бита ориентации бойца
                ; In:
                ;   IX - запись бойца
                ; Out:
                ;   бит 0 поля Side инвертирован, основной AF сохранён
                ; Corrupt:
                ;   AF'
                ; -----------------------------------------
Entry:          EX AF, AF'
                LD A, (IX + @FArchiveEngineFighter.Side)
                XOR @ArchiveEngineConst.FacingMask
                LD (IX + @FArchiveEngineFighter.Side), A
                EX AF, AF'
                RET

                endmodule
                endmodule
