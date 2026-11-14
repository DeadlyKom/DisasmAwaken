                module ArchiveEngine
                module ApplyFighterAction
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; подключение группы кадров BAR или повторное применение ожидающего шага
                ; In:
                ;   IX - запись бойца, запрос в диапазоне 0..35, BAR отображён в окно
                ; Out:
                ;   при смене группы загружены параметры заголовка и индекс первого шага
                ;   при ожидающем обновлении управление продолжается в ApplyFighterStep
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; Note:
                ;   действия #1C..#21 сохраняют старый индекс, действия 1 и 2 могут отражать индекс
                ;   действие #23 переключает сторону, отложенный разворот обрабатывается независимо
                ; -----------------------------------------
                ; проверка смены группы по сравнению запроса с загруженным действием
Entry:          LD A, (IX + @FArchiveEngineFighter.Request)
                CP (IX + @FArchiveEngineFighter.LoadedAction)
                JR Z, @ArchiveEngine.ApplyFighterAction.CheckPending            ; переход, если группа уже загружена, проверить ожидание шага

                ; выбор начального индекса для смены направления и для шести переходных действий
                LD B, #00
                CP #01
                CALL Z, @ArchiveEngine.ResumeLeftAction.Entry                   ; вызов, если запрошено действие 1, выбрать начальный индекс
                CP #02
                CALL Z, @ArchiveEngine.ResumeRightAction.Entry                  ; вызов, если запрошено действие 2, выбрать начальный индекс
                CP #1C
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #1C, сохранить прежний индекс
                CP #1D
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #1D, сохранить прежний индекс
                CP #1E
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #1E, сохранить прежний индекс
                CP #1F
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #1F, сохранить прежний индекс
                CP #20
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #20, сохранить прежний индекс
                CP #21
                CALL Z, @ArchiveEngine.ReuseFrameIndex.Entry                    ; вызов, если запрошено действие #21, сохранить прежний индекс

                ; проверка завершения разворота и сохранение нового действия
                CP #23
                CALL Z, @ArchiveEngine.FlipFighterSide.Entry                    ; вызов, если запрошено действие #23, переключить сторону
                LD (IX + @FArchiveEngineFighter.LoadedAction), A

                ; проверка отложенного разворота, выполняемого только при смене группы
                EX AF, AF'
                LD A, (IX + @FArchiveEngineFighter.TurnPending)
                OR A
                JR Z, @ArchiveEngine.ApplyFighterAction.ReadGroup               ; переход, если разворот не отложен, читать заголовок

                XOR A
                LD (IX + @FArchiveEngineFighter.TurnPending), A
                LD A, (IX + @FArchiveEngineFighter.Side)
                XOR @ArchiveEngineConst.FacingMask
                LD (IX + @FArchiveEngineFighter.Side), A

                ; поиск заголовка по относительному слову из таблицы BAR
ReadGroup:      EX AF, AF'
                LD E, (IX + @FArchiveEngineFighter.BarBase.Low)
                LD D, (IX + @FArchiveEngineFighter.BarBase.High)
                EX DE, HL
                PUSH HL
                LD E, A
                LD D, #00
                ADD HL, DE
                ADD HL, DE
                LD E, (HL)
                INC HL
                LD D, (HL)
                POP HL
                ADD HL, DE

                ; копирование четырёх полей заголовка и сохранение адреса первого шага
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.StepCount), A
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.ActionFlags), A
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.RepeatStep), A
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.NextAction), A
                LD D, H
                LD E, L
                LD (IX + @FArchiveEngineFighter.Steps.Low), E
                LD (IX + @FArchiveEngineFighter.Steps.High), D
                LD (IX + @FArchiveEngineFighter.StepIndex), B
                XOR A
                LD (IX + @FArchiveEngineFighter.FramePending), A
                JR @ArchiveEngine.ApplyFighterStep.Entry

                ; проверка необходимости применить шаг без смены группы
CheckPending:   LD A, (IX + @FArchiveEngineFighter.FramePending)
                OR A
                RET Z                                                           ; выход, если текущий шаг не требует обновления

                XOR A
                LD (IX + @FArchiveEngineFighter.FramePending), A

                ; JP ApplyFighterStep.Entry, продолжение в ApplyFighterStep.asm
                endmodule
                endmodule
