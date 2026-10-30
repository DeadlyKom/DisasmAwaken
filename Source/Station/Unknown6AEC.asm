                module Station
                module Unknown6AEC
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0D98..#0E39
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
                JP Z, @Station.Unknown6AEC.Point6B2C

                CALL #C85E
                JR NZ, @Station.Unknown6AEC.Point6B02

                LD BC, #9728
                LD DE, #99AE
                JP @Station.UnknownA191.Entry

Point6B02:      CALL @Station.Unknown6C00.Entry
                LD DE, (#6B8F)
                LD A, (#6B95)
                CALL @Station.UnknownA26F.Entry
                LD A, #FF
                LD (#6B95), A
                LD HL, #6BB6
                LD (#A265), HL
                LD HL, #000C
                LD (#A235), HL
                LD A, #08
                LD HL, #0000
                CALL @Station.UnknownA1D6.Entry
                LD (#6B23), HL
                RET

Point6B2C:      LD A, (#6B23)
                INC A
                RET Z

                DEC A
                LD C, A
                LD A, (#6B95)
                ADD A, C
                LD C, A
                LD B, #00
                LD HL, #9728
                ADD HL, BC
                LD A, C
                CP #04
                JR NC, @Station.Unknown6AEC.Point6B4F

                LD A, (HL)
                CP #59
                LD A, #4E
                JR Z, @Station.Unknown6AEC.Point6B4C

                LD A, #59
Point6B4C:      LD (HL), A
                JR @Station.Unknown6AEC.Point6B84

Point6B4F:      LD A, (HL)
                LD (HL), #5F
                CALL @Station.BeginScreenUpdate.Entry
                PUSH HL
                PUSH BC
                CALL @Station.Unknown6B9E.Entry
                CALL @Station.EndScreenUpdate.Entry
                POP BC
Point6B5E:      CALL @Station.ReadMatrixKey.Entry
                CP #1D
                JR Z, @Station.Unknown6AEC.Point6B5E

                LD E, A
                LD A, C
                CP #0A
                JR C, @Station.Unknown6AEC.Point6B82

                CP #0C
                LD A, E
                JR NC, @Station.Unknown6AEC.Point6B7A

                CP #30
                JR C, @Station.Unknown6AEC.Point6B5E

                CP #38
                JR NC, @Station.Unknown6AEC.Point6B5E

                JR @Station.Unknown6AEC.Point6B82

Point6B7A:      CP #30
                JR C, @Station.Unknown6AEC.Point6B5E

                CP #32
                JR NC, @Station.Unknown6AEC.Point6B5E

Point6B82:      POP HL
                LD (HL), E
Point6B84:      CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.Unknown6B9E.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
