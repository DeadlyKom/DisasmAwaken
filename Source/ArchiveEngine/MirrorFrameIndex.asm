                module ArchiveEngine
                module MirrorFrameIndex
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; пересчёт индекса при смене направления между действиями 1 и 2
                ; In:
                ;   BC - C, номер нового действия, IX - запись бойца
                ; Out:
                ;   B равен 9 минус прежний индекс, если байтовый результат меньше 9, иначе 8
                ;   C сохранён, A получает номер нового действия
                ; Corrupt:
                ;   BC, AF
                ; -----------------------------------------
                ; расчёт отражённого номера и проверка границы после байтового вычитания
Entry:          LD A, #09
                SUB (IX + @FArchiveEngineFighter.StepIndex)
                CP #09
                JR C, @ArchiveEngine.MirrorFrameIndex.StoreIndex                ; переход, если результат меньше девяти, использовать вычисленный индекс

                LD A, #08
StoreIndex:     LD B, A
                LD A, C
                RET

                endmodule
                endmodule
