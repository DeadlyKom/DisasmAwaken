                module ArchiveEngine
                module ApplyFighterStep
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; применение 14-байтового шага BAR и расчёт параметров вывода бойца
                ; In:
                ;   IX - запись бойца с адресом первого шага и индексом
                ;   BAR доступен в странице 0, положение окна и маска второй записи установлены
                ; Out:
                ;   изменены задержка, MoveX, позиция, координаты рисования, источник и адрес кадра
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; Note:
                ;   горизонтальное смещение и поправка отражаются в зависимости от стороны
                ;   расчёт координат использует младшие байты, точные проверки боковых пределов выделены отдельно
                ; -----------------------------------------
                ; расчёт адреса шага как Steps + 14 × StepIndex
Entry:          LD E, (IX + @FArchiveEngineFighter.StepIndex)
                LD D, #00
                SLA E
                RL D
                LD H, D
                LD L, E
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                OR A
                SBC HL, DE
                LD E, (IX + @FArchiveEngineFighter.Steps.Low)
                LD D, (IX + @FArchiveEngineFighter.Steps.High)
                ADD HL, DE

                ; чтение задержки и горизонтального смещения, сохранение адреса MoveY
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.StepTicks), A
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                PUSH HL
                LD (IX + @FArchiveEngineFighter.MoveX.Low), C
                LD (IX + @FArchiveEngineFighter.MoveX.High), B

                ; расчёт кандидата X с учётом стороны и проверка двух горизонтальных границ
                LD A, (IX + @FArchiveEngineFighter.PositionX)
                LD L, A
                LD H, #00
                CALL @ArchiveEngine.ApplySideDelta.Entry
                LD A, (@ArchiveEngineScene.View.ViewColumn)
                ADD A, #03
                CP L
                JP NC, @ArchiveEngine.ClampAtLeft.Entry                         ; переход, если X не больше левой границы, проверить противника

                ADD A, #18
                CP L
                JP C, @ArchiveEngine.ClampAtRight.Entry                         ; переход, если X больше правой границы, проверить противника

                ; сохранение кандидата внутри видимой области
                LD A, L
                LD (IX + @FArchiveEngineFighter.PositionX), A

                ; чтение вертикального перемещения и обновление базового Y
ReadOffsets:    POP HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                PUSH HL
                LD A, (IX + @FArchiveEngineFighter.PositionY)
                LD L, A
                LD H, #00
                ADD HL, BC
                LD A, L
                LD (IX + @FArchiveEngineFighter.PositionY), A

                ; применение горизонтальной поправки рисования с учётом стороны
                POP HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                PUSH HL
                LD A, (IX + @FArchiveEngineFighter.PositionX)
                LD L, A
                LD H, #00
                CALL @ArchiveEngine.ApplySideDelta.Entry
                LD A, L
                LD (IX + @FArchiveEngineFighter.DrawX), A

                ; применение вертикальной поправки рисования
                POP HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                PUSH HL
                LD A, (IX + @FArchiveEngineFighter.PositionY)
                LD L, A
                LD H, #00
                ADD HL, BC
                LD A, L
                LD (IX + @FArchiveEngineFighter.DrawY), A

                ; чтение индекса BD, адреса пары маска и рисунок, ширины и высоты
                POP HL
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.SpriteBank), A
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.FrameSource.Low), E
                LD (IX + @FArchiveEngineFighter.FrameSource.High), D
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.FrameWidth), A
                LD A, (HL)
                INC HL
                LD (IX + @FArchiveEngineFighter.FrameHeight), A

                ; расчёт адреса кадра как начало сцены плюс смещение строки и столбца
                LD A, (IX + @FArchiveEngineFighter.DrawY)
                LD HL, @ArchiveEngineScene.View.SpriteYBias
                ADD A, (HL)
                LD DE, (@ArchiveEngineScene.View.RowBytes)
                CALL @ArchiveEngine.MultiplyByteWord.Entry
                LD E, (IX + @FArchiveEngineFighter.DrawX)
                LD D, #00
                ADD HL, DE
                LD DE, @ArchiveEngineConst.ScenePixels
                ADD HL, DE
                LD D, H
                LD E, L
                LD (IX + @FArchiveEngineFighter.FrameDest.Low), E
                LD (IX + @FArchiveEngineFighter.FrameDest.High), D
                RET

                endmodule
                endmodule
