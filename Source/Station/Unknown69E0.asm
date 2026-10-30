                module Station
                module Unknown69E0
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0C8C..#0CF6
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
                JP Z, @Station.Unknown69E0.Point6A1E

                CALL #C85E
                JR NZ, @Station.Unknown69E0.Point69F4

                LD DE, (#69A9)
                JP #C873

Point69F4:      CALL @Station.Unknown6A7E.Entry
                LD DE, (#6A4C)
                LD A, (#6A52)
                CALL @Station.UnknownA26F.Entry
                LD A, #FF
                LD (#6A52), A
                LD HL, #6A6C
                LD (#A265), HL
                LD HL, #0007
                LD (#A235), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#6A15), HL
                RET

Point6A1E:      LD A, (#6A15)
                INC A
                RET Z

                DEC A
                LD C, A
                LD HL, #0000
                LD (#699D), HL
                LD A, (#6A52)
                ADD A, C
                EX AF, AF'
                LD A, #17
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                CALL #DB57
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem23.Entry
                CALL @Station.DrawItem22.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
