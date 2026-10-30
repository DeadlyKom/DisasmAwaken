                module Station
                module Unknown6FF1
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #129D..#12EF
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
                JP Z, @Station.Unknown6FF1.Point702F

                CALL #C85E
                JR NZ, @Station.Unknown6FF1.Point7005

                LD DE, (#7D78)
                JP #C873

Point7005:      CALL @Station.Unknown7154.Entry
                LD DE, (#7062)
                LD A, (#7068)
                CALL @Station.UnknownA26F.Entry
                LD A, #FF
                LD (#7068), A
                LD HL, #708E
                LD (#A265), HL
                LD HL, #001D
                LD (#A235), HL
                LD A, #20
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#7026), HL
                RET

Point702F:      LD A, (#7068)
                INC A
                RET Z

                LD HL, (#6307)
                LD A, (#AEBB)
                SUB L
                NEG
                CP #87
                LD A, #0A
                JR C, @Station.Unknown7044.Entry

                DEC A
                ; JP @Station.Unknown7044.Entry, продолжение в Unknown7044.asm

                endmodule
                endmodule
