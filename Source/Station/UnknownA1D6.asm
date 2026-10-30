                module Station
                module UnknownA1D6
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #41D6..#426E
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          LD (#C6E3), A
                LD C, A
                PUSH BC
                PUSH HL
                LD A, #17
                CALL @Station.SelectMemoryPage.Entry
                LD HL, #5800
                LD DE, #D800
                LD BC, #0300
                LDIR
                LD A, #10
                CALL @Station.SelectMemoryPage.Entry
                POP HL
                POP BC
                LD A, (#AEAB)
                SUB C
                RET C

                RET Z

                LD (#A25E), A
                RRA
                RRA
                RRA
                AND #1F
                LD C, A
                LD DE, (#6307)
                PUSH DE
                CALL @Station.SuspendPointer.Entry
PointA20A:      CALL @Station.MergeActionInputs.Entry
                JR Z, @Station.UnknownA191.PointA1CD

                LD A, C
                AND A
                JR Z, @Station.UnknownA1D6.PointA20A

                LD A, (#6308)
                LD D, A
                LD A, (#AEC7)
                LD E, A
                LD A, (#AEAB)
                SRL A
                ADD A, E
                LD B, A
                LD A, (#C6E3)
                SRL A
                ADD A, B
                CP D
                JP C, @Station.UnknownA1D6.PointA234

                LD A, L
                OR H
                JR Z, @Station.UnknownA1D6.PointA20A

                DEC HL
                JP @Station.UnknownA1D6.PointA245

PointA234:      LD DE, #0000
                EX DE, HL
                OR A
                SBC HL, DE
                LD B, #00
                SBC HL, BC
                EX DE, HL
                JR Z, @Station.UnknownA1D6.PointA20A

                JR C, @Station.UnknownA1D6.PointA20A

                INC HL
PointA245:      PUSH BC
                PUSH HL
                LD A, #17
                CALL @Station.SelectMemoryPage.Entry
                LD HL, #4000
                LD DE, #C000
                LD BC, #1800
                LDIR
                LD A, #18
                CALL @Station.SelectMemoryPage.Entry
                HALT
                LD A, #00
                CALL @Station.UnknownC6B0.Entry
                POP HL
                PUSH HL
                CALL #0000
                POP HL
                CALL @Station.EndScreenUpdate.ShowBase
                POP BC
                JP @Station.UnknownA1D6.PointA20A

                endmodule
                endmodule
