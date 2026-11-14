                module ArchiveEngine
                module AdvanceFighterFrames
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; обновление счётчиков анимации обеих записей бойцов
                ; In:
                ;   обе записи содержат запросы, текущие индексы и задержки
                ; Out:
                ;   задержки и запросы обработаны для обоих бойцов, IX указывает на второго
                ; Corrupt:
                ;   AF, IX
                ; -----------------------------------------
Entry:          LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.AdvanceFighterStep.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.AdvanceFighterStep.Entry
                RET

                endmodule
                endmodule
