                module Station
                module UnknownC6B0
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #66B0..#685D
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          PUSH AF
                LD A, (#AEB3)
                LD E, A
                LD A, (#AEBB)
                LD C, A
                EXX
                LD A, (#AEBF)
                LD C, A
                EXX
                AND A
                LD A, C
                JP P, @Station.UnknownC6B0.PointC6CD

                ADD A, E
                ADD A, #08
                LD E, A
                LD C, #00
                JP @Station.UnknownC6B0.PointC6DB

PointC6CD:      DEC A
                ADD A, E
                JP NC, @Station.UnknownC6B0.PointC6DB

                EXX
                LD C, #01
                EXX
                CPL
                ADD A, E
                ADD A, #08
                LD E, A
PointC6DB:      POP AF
                ADD A, #05
                LD D, A
                LD A, (#AEC7)
                ADD A, #00
                LD B, A
                LD A, (#AECB)
                AND A
                LD A, B
                JP P, @Station.UnknownC6B0.PointC6FC

                ADD A, D
                RET Z

                CP #C0
                RET NC

                BIT 7, B
                JR Z, @Station.UnknownC6B0.PointC70C

                LD B, #00
                LD D, A
                JP @Station.UnknownC6B0.PointC70C

PointC6FC:      CP #C0
                RET NC

                ADD A, D
                JR C, @Station.UnknownC6B0.PointC706

                CP #C0
                JR C, @Station.UnknownC6B0.PointC70C

PointC706:      SUB #BF
                NEG
                ADD A, D
                LD D, A
PointC70C:      LD H, #82
                LD L, B
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, C
                OR (HL)
                LD L, A
                LD H, B
                LD B, E
                SRL E
                SRL E
                SRL E
                LD A, E
                SUB #01
                RET C

                LD E, A
                LD A, B
                AND #07
                JR NZ, @Station.UnknownC6B0.PointC72D

                LD A, E
                SUB #01
                RET C

                LD E, A
PointC72D:      LD A, #1E
                SUB E
                ADD A, A
                LD (#C754), A
                LD (#C7AE), A
                LD (#C80B), A
                LD E, #07
                LD B, #07
                EXX
                INC C
                EXX
                JP Z, @Station.UnknownC6B0.PointC7AB

                LD B, #E0
                EXX
                DEC C
                DEC C
                EXX
                JP Z, @Station.UnknownC6B0.PointC804

PointC74D:      LD C, L
                LD A, (HL)
                AND B
                LD (HL), A
                INC L
                XOR A
                JR @Station.UnknownC6B0.PointC755

PointC755:      LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, (HL)
                AND #07
                LD (HL), A
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.UnknownC6B0.PointC7A6

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Station.UnknownC6B0.PointC7A6

                LD A, H
                SUB #08
                LD H, A
PointC7A6:      DEC D
                JP NZ, @Station.UnknownC6B0.PointC74D

                RET

PointC7AB:      LD C, L
                XOR A
                JR @Station.UnknownC6B0.PointC7AF

PointC7AF:      LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, (HL)
                AND B
                LD (HL), A
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.UnknownC6B0.PointC7FF

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Station.UnknownC6B0.PointC7FF

                LD A, H
                SUB #08
                LD H, A
PointC7FF:      DEC D
                JP NZ, @Station.UnknownC6B0.PointC7AB

                RET

PointC804:      LD C, L
                LD A, (HL)
                AND B
                LD (HL), A
                INC L
                XOR A
                JR @Station.UnknownC6B0.PointC80C

PointC80C:      LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD L, C
                INC H
                LD A, H
                AND E
                JP NZ, @Station.UnknownC6B0.PointC859

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Station.UnknownC6B0.PointC859

                LD A, H
                SUB #08
                LD H, A
PointC859:      DEC D
                JP NZ, @Station.UnknownC6B0.PointC804

                RET

                endmodule
                endmodule
