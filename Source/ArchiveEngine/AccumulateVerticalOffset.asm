                module ArchiveEngine
                module AccumulateVerticalOffset
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; расчёт требуемого вертикального смещения по нижней строке кадра
                ; In:
                ;   BC - B, прежний максимум, IX - запись бойца
                ; Out:
                ;   если сумма DrawY и FrameHeight по модулю байта не меньше 166, кандидат ограничен MaxVertical
                ;   если кандидат не меньше B, B и VerticalOffset получают этот кандидат
                ; Corrupt:
                ;   HL, BC, AF
                ; -----------------------------------------
                ; вычисление нижней строки кадра и проверка порога смещения
Entry:          LD A, (IX + @FArchiveEngineFighter.DrawY)
                LD C, A
                LD A, (IX + @FArchiveEngineFighter.FrameHeight)
                ADD A, C
                CP #A6
                RET C                                                           ; выход, если нижняя строка меньше порога 166

                ; ограничение кандидата максимальным смещением окна
                SUB #A6
                LD HL, @ArchiveEngineScene.View.MaxVertical
                CP (HL)
                JR C, @ArchiveEngine.AccumulateVerticalOffset.CompareMaximum    ; переход, если кандидат меньше предела, оставить его

                LD A, (HL)

                ; проверка накопленного максимума перед записью
CompareMaximum: CP B
                RET C                                                           ; выход, если кандидат меньше ранее найденного смещения

                LD (@ArchiveEngineScene.View.VerticalOffset), A
                LD B, A
                RET

                endmodule
                endmodule
