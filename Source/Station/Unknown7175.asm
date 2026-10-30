                module Station
                module Unknown7175
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #1421..#14BB
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
                JP Z, @Station.Unknown7175.Point71C2

                CALL #C85E
                JR NZ, @Station.Unknown7175.Point7198

                LD DE, (#7B26)
                CALL #C873
                LD DE, (#7B41)
                CALL #C873
                LD DE, (#6AB7)
                CALL #C873
                RET

Point7198:      CALL @Station.Unknown733F.Entry
                LD DE, (#7211)
                LD A, (#7217)
                CALL @Station.UnknownA26F.Entry
                LD A, #FF
                LD (#7217), A
                LD HL, #7244
                LD (#A265), HL
                LD HL, #001D
                LD (#A235), HL
                LD A, #18
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#71B9), HL
                RET

Point71C2:      LD A, (#7217)
                INC A
                RET Z

                DEC A
                LD L, A
                LD A, (#71B9)
                ADD A, L
                LD L, A
                LD A, (#6ACC)
                CP L
                JR Z, @Station.Unknown7175.Point71EB

                LD A, L
                LD (#6ACC), A
                LD HL, #0000
                LD (#6AA4), HL
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.Unknown6AAF.Entry
                CALL @Station.Unknown7220.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

Point71EB:      LD A, #00
                OR A
                LD A, #05
                JR Z, @Station.Unknown7175.Point71F3

                INC A
Point71F3:      LD (#983A), A
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                CALL #C000
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.DrawItem38.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
