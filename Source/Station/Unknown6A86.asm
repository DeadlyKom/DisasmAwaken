                module Station
                module Unknown6A86
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0D32..#0D59
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
                JP Z, @Station.Unknown6A86.Point6AAD

                CALL #C85E
                RET Z

                CALL @Station.Unknown6AC6.Entry
                LD HL, #6ADE
                LD (#A265), HL
                LD HL, #0000
                LD (#A235), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#6AA4), HL
                RET

Point6AAD:      RET

                endmodule
                endmodule
