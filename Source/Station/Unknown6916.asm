                module Station
                module Unknown6916
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0BC2..#0BE8
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
                JR Z, @Station.Unknown6916.Point693C

                CALL #C85E
                RET Z

                CALL @Station.Unknown6963.Entry
                LD HL, #6952
                LD (#A265), HL
                LD HL, #0000
                LD (#A235), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#6933), HL
                RET

Point693C:      RET

                endmodule
                endmodule
