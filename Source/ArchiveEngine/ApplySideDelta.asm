                module ArchiveEngine
                module ApplySideDelta
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; применение горизонтального смещения с учётом ориентации
                ; In:
                ;   HL - координата, BC - знаковая поправка, IX - запись бойца
                ; Out:
                ;   HL - координата с поправкой, прямая сторона прибавляет, зеркальная вычитает
                ; Corrupt:
                ;   HL, AF
                ; -----------------------------------------
                ; проверка стороны перед выбором знака поправки
Entry:          LD A, (IX + @FArchiveEngineFighter.Side)
                OR A
                JR Z, @ArchiveEngine.ApplySideDelta.AddDelta                    ; переход, если сторона прямая, прибавить поправку

                SBC HL, BC
                RET

AddDelta:       ADD HL, BC
                RET

                endmodule
                endmodule
