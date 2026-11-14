                module ArchiveEngine
                module ReconcileFacing
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; проверка стороны обоих бойцов при разных базовых Y
                ; In:
                ;   обе рабочие записи бойцов доступны
                ; Out:
                ;   запрос разворота проверен сначала для второго, затем для первого бойца
                ; Corrupt:
                ;   BC, AF, IX
                ; -----------------------------------------
Entry:          CALL @ArchiveEngine.CheckSecondFacing.Entry
                CALL @ArchiveEngine.CheckFirstFacing.Entry
                RET

                endmodule
                endmodule
