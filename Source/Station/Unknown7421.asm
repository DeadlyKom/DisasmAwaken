                module Station
                module Unknown7421
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #16CD..#172D
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
                JP Z, @Station.Unknown7421.Point742E

                CALL #C85E
                RET Z

                RET

Point742E:      LD A, I
                LD (#7471), A
                DI
                LD A, #3F
                LD I, A
                IM 1
                PUSH IY
                PUSH HL
                PUSH AF
                PUSH DE
                LD IY, #5C3A
                LD A, (@PanelHoverState.ToPositionRow)
                ADD A, #30
                LD HL, #7534
                LD (HL), A
                LD HL, #7530
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD C, #0A
                CALL #3D13
                LD A, C
                LD C, #08
                CALL #3D13
                LD HL, #983B
                LD DE, (#5CEB)
                LD B, #02
                LD C, #06
                CALL #3D13
                LD A, #00
                LD I, A
                IM 2
                POP DE
                POP AF
                POP HL
                POP IY
                CALL #C873
                LD A, (@PanelHoverState.ToPositionRow)
                RET

                endmodule
                endmodule
