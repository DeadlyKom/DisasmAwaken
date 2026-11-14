                module ArchiveEngine
                module ResumeRightAction
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; выбор преобразованного индекса при запросе действия 2 после действия 1
                ; In:
                ;   BC - B, индекс по умолчанию, AF - A, новый запрос
                ;   IX - запись бойца
                ; Out:
                ;   B изменяется только при загруженном действии 1, A сохраняется
                ; Corrupt:
                ;   BC, AF
                ; -----------------------------------------
                ; проверка, что переход идёт с противоположного направления
Entry:          LD C, A
                LD A, (IX + @FArchiveEngineFighter.LoadedAction)
                CP #01
                JR Z, @ArchiveEngine.MirrorFrameIndex.Entry                     ; переход, если загружено действие 1, пересчитать индекс

                LD A, C
                RET

                endmodule
                endmodule
