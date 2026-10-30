                module Station
                module Unknown759C
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #1848..#18CB
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
                JP Z, @Station.Unknown759C.Point75DC

                CALL #C85E
                JR NZ, @Station.Unknown759C.Point75B2

                LD BC, #9736
                LD DE, #99C8
                JP @Station.UnknownA191.Entry

Point75B2:      CALL @Station.Unknown766C.Entry
                LD DE, (#7621)
                LD A, (#7627)
                CALL @Station.UnknownA26F.Entry
                LD A, #FF
                LD (#7627), A
                LD HL, #7648
                LD (#A265), HL
                LD HL, #001A
                LD (#A235), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#75D3), HL
                RET

Point75DC:      LD A, (#75D3)
                INC A
                RET Z

                DEC A
                LD C, A
                LD A, (#7627)
                ADD A, C
                LD C, A
                LD B, #00
                LD HL, #9736
                ADD HL, BC
                LD A, C
                AND A
                JR NZ, @Station.Unknown759C.Point75FE

                LD A, (HL)
                CP #59
                LD A, #4E
                JR Z, @Station.Unknown759C.Point75FB

                LD A, #59
Point75FB:      LD (HL), A
                JR @Station.Unknown759C.Point7616

Point75FE:      LD A, (HL)
                LD (HL), #5F
                CALL @Station.BeginScreenUpdate.Entry
                PUSH HL
                PUSH BC
                CALL @Station.DrawItem42.Entry
                CALL @Station.EndScreenUpdate.Entry
                POP BC
Point760D:      CALL @Station.ReadMatrixKey.Entry
                CP #1D
                JR Z, @Station.Unknown759C.Point760D

                POP HL
                LD (HL), A
Point7616:      CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.Unknown7630.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
