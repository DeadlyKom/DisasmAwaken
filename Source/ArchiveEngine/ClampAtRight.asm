                module ArchiveEngine
                module ClampAtRight
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; проверка соседа и сдвиг окна при выходе кандидата X к правому краю
                ; In:
                ;   HL - L, кандидат X, IX - запись текущего бойца
                ;   на стеке сохранён адрес MoveY из текущего шага
                ; Out:
                ;   управление продолжает чтение шага, X сохраняется или становится ViewX + 27
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; Note:
                ;   выражение X минус 23 вычисляется по модулю 256
                ; -----------------------------------------
                ; расчёт адреса противоположного бойца через XOR двух адресов
Entry:          EX AF, AF'
                LD A, (@ArchiveOpponentMask.Value.Low)
                XOR IXL
                LD E, A
                LD A, (@ArchiveOpponentMask.Value.High)
                XOR IXH
                LD D, A
                EX AF, AF'

                ; проверка расстояния от кандидата до противоположного бойца
                LD A, L
                SUB #17
                LD HL, @FArchiveEngineFighter.PositionX
                ADD HL, DE
                CP (HL)
                JP NC, @ArchiveEngine.ApplyFighterStep.ReadOffsets              ; переход, если X минус 23 не меньше X противника, сохранить прежнюю позицию

                ; сдвиг окна вправо и фиксация бойца у новой границы
                CALL @ArchiveEngine.MoveViewRight.Entry
                LD A, (@ArchiveEngineScene.View.ViewColumn)
                ADD A, #1B
                LD (IX + @FArchiveEngineFighter.PositionX), A
                JP @ArchiveEngine.ApplyFighterStep.ReadOffsets

                endmodule
                endmodule
