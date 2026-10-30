                module Station
                module Unknown683A
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0AE6..#0B1A
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          CALL @Station.RepaintAndTrack.Entry
                RET C

                DEC A
                JR Z, @Station.Unknown683A.Point685E

                CALL #C85E
                JR NZ, @Station.Unknown683A.Point684D

                LD HL, #9A58
                LD (#9A89), HL
                RET

Point684D:      LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD HL, #0020
                CALL #E0B5
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET

Point685E:      LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD HL, #FFE0
                CALL #E0B5
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET

                endmodule
                endmodule
