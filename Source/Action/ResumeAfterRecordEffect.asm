                module Action
                module ResumeAfterRecordEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordEffectResume.md)
                ; -----------------------------------------
                ; Сброс флагов связи и продолжение обхода объектов
                ; исходная запись 17, адреса F7BF..F7C5
                ; In:
                ;   IX указывает исходную запись после PrepareLargeEffect, SP восстановлен
                ; Out:
                ;   LinkFlags получает ноль, управление передано F735 без нового возврата
                ; Corrupt:
                ;   LinkFlags и R, остальные регистры, AF и SP сохраняются
                ; Note:
                ;   семь исходных байтов выполняются непосредственно после CALL PrepareLargeEffect
                ; -----------------------------------------
                ; Сброс флагов связи освобождённой записи перед продолжением обхода.
Entry:          LD (IX + @FActionRecord.LinkFlags), #00
                JP @Action.UpdateObjects.PointF735

                endmodule
                endmodule
