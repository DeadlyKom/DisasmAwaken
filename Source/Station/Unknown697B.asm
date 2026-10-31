                module Station
                module Unknown697B
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0C27..#0C52
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
                JR Z, @Station.Unknown697B.Point69A6

                CALL #C85E
                JR NZ, @Station.Unknown697B.Point698E

                LD DE, (#6A5C)
                JP #C873

Point698E:      LD HL, #69CF
                LD (@ScrollState.RenderCall), HL
                LD HL, #0000
                LD (@ScrollState.EndLimit), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                LD (#699D), HL
                RET

Point69A6:      RET

                endmodule
                endmodule
