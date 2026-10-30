                module Station
                module UnknownA26F
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #426F..#427F
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          INC A
                RET Z

                DEC A
                PUSH AF
                CALL @Station.ClampRowHeight.Entry
                CALL @Station.SuspendPointer.Entry
                POP AF
                CALL @Station.XorItemRow.Entry
                JP @Station.ResumePointer.Entry

                endmodule
                endmodule
