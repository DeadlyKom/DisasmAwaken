                module ArchiveEngine
                module ClampAtLeft
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; проверка соседа и сдвиг окна при выходе кандидата X к левому краю
                ; In:
                ;   HL - L, кандидат X, IX - запись текущего бойца
                ;   на стеке сохранён адрес MoveY из текущего шага
                ; Out:
                ;   управление продолжает чтение шага, X сохраняется или становится ViewX + 4
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; Note:
                ;   выражение X + 23 вычисляется по модулю 256
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
                ADD A, #17
                LD HL, @FArchiveEngineFighter.PositionX
                ADD HL, DE
                CP (HL)
                JP C, @ArchiveEngine.ApplyFighterStep.ReadOffsets               ; переход, если X плюс 23 меньше X противника, сохранить прежнюю позицию

                ; сдвиг окна влево и фиксация бойца у новой границы
                CALL @ArchiveEngine.MoveViewLeft.Entry
                LD A, (@ArchiveEngineScene.View.ViewColumn)
                ADD A, #04
                LD (IX + @FArchiveEngineFighter.PositionX), A
                JP @ArchiveEngine.ApplyFighterStep.ReadOffsets

                endmodule
                endmodule
