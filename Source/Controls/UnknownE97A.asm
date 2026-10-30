                module Controls
                module UnknownE97A
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #0E9C..#102F
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          EX AF, AF'
                LD A, (#8431)
                XOR #FE
                LD (#8431), A
                LD A, (#87F1)
                XOR #FE
                LD (#87F1), A
                LD A, (#842E)
                XOR #FE
                LD (#842E), A
                LD A, (#87EE)
                XOR #FE
                LD (#87EE), A
                LD HL, #844E
                LD DE, #8451
                LD BC, #0020
                EXX
                LD L, #07
PointE9A7:      EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #02
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.UnknownE97A.PointE9A7                          ; переход, если флаг Z сброшен


                EXX
                LD HL, #870E
                LD DE, #8711
                EXX
                LD L, #07
PointE9C3:      EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #02
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.UnknownE97A.PointE9C3                          ; переход, если флаг Z сброшен


                EX AF, AF'
                DEC A
                RET Z                                                           ; выход, если флаг Z установлен

                LD HL, #8116
                LD B, #0E
PointE9DD:      LD A, (HL)
                CPL
                LD (HL), A
                DEC L
                DJNZ @Controls.UnknownE97A.PointE9DD

                LD HL, #8129
                LD DE, #8136
                LD BC, #0020
                EXX
                LD L, #57
PointE9EF:      EXX
                LD A, #80
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                LD A, #01
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                EX DE, HL
                EXX
                DEC L
                JP NZ, @Controls.UnknownE97A.PointE9EF                          ; переход, если флаг Z сброшен


                LD DE, #0040
                LD IX, #A0C0
                JP @Controls.UnknownE97A.PointEA11


PointEA0B:      LD A, (IX + #00)
                CP #80
                RET Z                                                           ; выход, если флаг Z установлен

PointEA11:      LD DE, #0040
PointEA14:      ADD IX, DE
                LD A, (IX + #01)
                CP #80
                JR Z, @Controls.UnknownE97A.PointEA0B                           ; переход, если флаг Z установлен


                LD A, (IX + #12)
                CP #14
                JR Z, @Controls.UnknownE97A.PointEA0B                           ; переход, если флаг Z установлен


                LD A, (IX + #1B)
                CP #80
                JR Z, @Controls.UnknownE97A.PointEA14                           ; переход, если флаг Z установлен


                LD B, A
                LD C, (IX + #1A)
                LD D, (IX + #1F)
                BIT 7, D
                JR NZ, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Z сброшен


                LD A, D
                CP #06
                JR C, @Controls.UnknownE97A.PointEA11                           ; переход, если флаг Carry установлен


                LD E, (IX + #1E)
                LD A, (IX + #1D)
                LD H, A
                LD L, (IX + #1C)
                CALL #ADC5
                JR NZ, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Z сброшен


                LD A, H
                AND A
                JR NZ, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Z сброшен


                LD A, D
                AND A
                JR NZ, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Z сброшен


                LD A, L
                SUB #50
                JR C, @Controls.UnknownE97A.PointEA11                           ; переход, если флаг Carry установлен


                CP #5E
                JR NC, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Carry сброшен


                LD A, E
                SUB #0E
                JR C, @Controls.UnknownE97A.PointEA11                           ; переход, если флаг Carry установлен


                CP #4C
                JR NC, @Controls.UnknownE97A.PointEA11                          ; переход, если флаг Carry сброшен


                LD B, E
                LD A, L
                SUB #04
                LD C, A
                AND #07
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, #0E
                LD E, A
                LD A, #EB
                ADC A, #00
                LD D, A
                LD A, IXL
                LD L, A
                LD A, IXH
                LD H, A
                PUSH DE
                LD DE, #5F00
                ADD HL, DE
                POP DE
                LD A, H
                SLA L
                RLA
                SLA L
                RLA
                LD L, A
                LD A, (#9B1B)
                CP L
                JR Z, @Controls.UnknownE97A.PointEA9D                           ; переход, если флаг Z установлен


                LD A, (#9B1C)
                CP L
                JR Z, @Controls.UnknownE97A.PointEA9D                           ; переход, если флаг Z установлен


                LD A, (#9B1D)
                CP L
                JR NZ, @Controls.UnknownE97A.PointEAA5                          ; переход, если флаг Z сброшен


PointEA9D:      LD A, E
                ADD A, #80
                LD E, A
                LD A, D
                ADC A, #00
                LD D, A
PointEAA5:      LD A, C
                RRCA
                RRCA
                RRCA
                AND #1F
                LD C, A
                LD A, B
                SUB #04
                RLCA
                LD L, A
                LD H, #08
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD B, #00
                ADD HL, BC
                LD BC, #001F
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                JP @Controls.UnknownE97A.PointEA11


                endmodule
                endmodule
