                module Station
                module Unknown6DC5
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #1071..#107E
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
                JP Z, @Station.Unknown6DC5.Point6DD2

                CALL #C85E
                RET Z

                RET

Point6DD2:      RET

                endmodule
                endmodule
