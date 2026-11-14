                module ArchiveEngine
                module AdvanceFighterStep
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; отсчёт задержки кадра и выбор дальнейшего индекса или действия
                ; In:
                ;   IX - рабочая запись бойца с уже загруженной группой
                ; Out:
                ;   при новом запросе задержка сохранена и установлен FramePending
                ;   при нулевом остатке индекс продвигается, повторяется или сбрасывается при смене действия
                ; Corrupt:
                ;   AF
                ; Note:
                ;   нулевая исходная задержка после DEC даёт #FF, сложение индекса байтовое
                ; -----------------------------------------
                ; проверка смены запроса перед изменением текущей задержки
Entry:          LD A, (IX + @FArchiveEngineFighter.Request)
                CP (IX + @FArchiveEngineFighter.LoadedAction)
                JR NZ, @ArchiveEngine.AdvanceFighterStep.NewRequest             ; переход, если запрошено другое действие, пометить загрузку

                ; уменьшение задержки и проверка истечения текущего кадра
                LD A, (IX + @FArchiveEngineFighter.StepTicks)
                DEC A
                LD (IX + @FArchiveEngineFighter.StepTicks), A
                RET NZ                                                          ; выход, если остаток задержки ненулевой

                ; пометка нового кадра и проверка выхода за число шагов
                LD A, #01
                LD (IX + @FArchiveEngineFighter.FramePending), A
                LD A, (IX + @FArchiveEngineFighter.StepIndex)
                INC A
                LD (IX + @FArchiveEngineFighter.StepIndex), A
                CP (IX + @FArchiveEngineFighter.StepCount)
                RET C                                                           ; выход, если новый индекс ещё внутри текущей группы

                ; проверка бита повтора при достижении конца группы
                BIT @ArchiveEngineConst.ActionRepeatBit, (IX + @FArchiveEngineFighter.ActionFlags)
                JR Z, @ArchiveEngine.AdvanceFighterStep.LoadNext                ; переход, если повтор выключен, запросить следующее действие

                LD A, (IX + @FArchiveEngineFighter.RepeatStep)
                LD (IX + @FArchiveEngineFighter.StepIndex), A
                RET

                ; запрос следующего действия и сброс индекса
LoadNext:       LD A, (IX + @FArchiveEngineFighter.NextAction)
                LD (IX + @FArchiveEngineFighter.Request), A
                XOR A
                LD (IX + @FArchiveEngineFighter.StepIndex), A
                RET

                ; пометка перехода без изменения задержки прежнего действия
NewRequest:     LD A, #01
                LD (IX + @FArchiveEngineFighter.FramePending), A
                RET

                endmodule
                endmodule
