                module Station
                module Unknown74AA
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #1756..#17B6
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
                JP Z, @Station.Unknown74AA.Point74B7

                CALL #C85E
                RET Z

                RET

Point74B7:      LD A, (@PanelHoverState.FromPositionRow)
                ADD A, #30
                LD HL, #7534
                LD (HL), A
                LD A, I
                LD (#74FF), A
                DI
                LD A, #3F
                LD I, A
                IM 1
                PUSH HL
                PUSH DE
                PUSH AF
                PUSH IY
                LD IY, #5C3A
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
                LD C, #05
                CALL #3D13
                POP IY
                POP AF
                POP DE
                POP HL
                LD A, #00
                LD I, A
                IM 2
                CALL #C873
                LD A, (@PanelHoverState.FromPositionRow)
                RET

                endmodule
                endmodule
