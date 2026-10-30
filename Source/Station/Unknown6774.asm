                module Station
                module Unknown6774
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0A20..#0A2B
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C

                DEC A
                JR Z, @Station.Unknown67A9.Point67AA

                CALL #C85E
                JR NZ, @Station.Unknown67A9.Entry

                ; JP @Station.Unknown6780.Entry, продолжение в Unknown6780.asm

                endmodule
                endmodule
