                module Controls
                module UnknownE291
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #07B3..#0B7E
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
Entry:          LD IX, #A0C0
                LD (#E48F), SP
                LD HL, (#A78F)
                SRA H
                RR L
                SRA H
                RR L
                LD A, L
                BIT 7, L
                LD B, #01
                JR Z, @Controls.UnknownE291.PointE2AF                           ; переход, если флаг Z установлен


                LD B, #FF
                NEG
PointE2AF:      LD L, #00
                ADD A, L
                LD (#E2B0), A
                LD C, #00
                JP NC, @Controls.UnknownE291.PointE2BB                          ; переход, если флаг Carry сброшен


                LD C, B
PointE2BB:      LD A, #00
                SUB C
                EXX
                AND #0F
                LD (#E2BC), A
                LD (#E471), A
                RLCA
                LD L, A
                LD H, #00
                LD B, H
                LD SP, #E271
                ADD HL, SP
                LD SP, HL
                LD HL, #48B2
                LD DE, #5555
                LD A, #05
                EX AF, AF'
                RET


                EX AF, AF'
PointE2DC:      EX AF, AF'
                LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE2F6                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE2F6                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE2F6:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE30F                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE30F                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE30F:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE328                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE328                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE328:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE341                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE341                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE341:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE35A                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE35A                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE35A:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE373                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE373                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE373:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE38C                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE38C                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE38C:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3A5                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3A5                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE3A5:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3BE                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3BE                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE3BE:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3D7                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3D7                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE3D7:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE3F0                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE3F0                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE3F0:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE409                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE409                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE409:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE422                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE422                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE422:      LD C, #00
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE43B                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE43B                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE43B:      LD C, #80
                LD SP, HL
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                PUSH BC
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE454                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE454                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE454:      LD SP, HL
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                PUSH DE
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE291.PointE46B                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE291.PointE46B                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE46B:      EX AF, AF'
                DEC A
                JP NZ, @Controls.UnknownE291.PointE2DC                          ; переход, если флаг Z сброшен


                LD A, #00
                AND A
                JR Z, @Controls.UnknownE291.PointE48E                           ; переход, если флаг Z установлен


                EX DE, HL
                LD L, A
                LD A, #10
                SUB L
                RLCA
                LD L, A
                XOR A
                LD H, A
                LD (#E471), A
                LD SP, #E271
                ADD HL, SP
                LD SP, HL
                LD A, #01
                LD HL, #5555
                EX DE, HL
                EX AF, AF'
                RET


PointE48E:      LD SP, #0000
                LD HL, #572C
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                LD HL, #504C
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                INC H
                DEC L
                SET 0, (HL)
                INC L
                SET 7, (HL)
                SET 6, (HL)
                JP @Controls.UnknownE291.PointE4B7


PointE4B1:      LD A, (IX + #00)
                CP #80
                RET Z                                                           ; выход, если флаг Z установлен

PointE4B7:      LD DE, #0040
PointE4BA:      ADD IX, DE
                LD A, (IX + #01)
                CP #80
                JR Z, @Controls.UnknownE291.PointE4B1                           ; переход, если флаг Z установлен


                LD A, (IX + #12)
                CP #14
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если флаг Z установлен


                CP #15
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если флаг Z установлен


                LD A, (IX + #1B)
                CP #80
                JR Z, @Controls.UnknownE291.PointE4BA                           ; переход, если флаг Z установлен


                LD C, A
                AND A
                JP P, @Controls.UnknownE291.PointE4DC                           ; переход, если флаг Sign сброшен


                NEG
PointE4DC:      CP #80
                JR NC, @Controls.UnknownE291.PointE4BA                          ; переход, если флаг Carry сброшен


                LD A, (IX + #1D)
                LD B, A
                AND A
                JP P, @Controls.UnknownE291.PointE4EA                           ; переход, если флаг Sign сброшен


                NEG
PointE4EA:      CP #80
                JR NC, @Controls.UnknownE291.PointE4BA                          ; переход, если флаг Carry сброшен


                LD A, (IX + #1F)
                LD E, A
                AND A
                JP P, @Controls.UnknownE291.PointE4F8                           ; переход, если флаг Sign сброшен


                NEG
PointE4F8:      CP #80
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если флаг Carry сброшен


                LD A, E
                LD E, C
                NEG
                LD C, A
                SRA C
                SRA C
                LD A, C
                SRA C
                ADC A, C
                LD C, A
                SRA E
                SRA E
                LD A, E
                SRA E
                ADC A, E
                LD E, A
                LD A, #90
                ADD A, C
                CP #B5
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если флаг Carry сброшен


                CP #6B
                JR C, @Controls.UnknownE291.PointE4B7                           ; переход, если флаг Carry установлен


                LD C, A
                LD A, #68
                ADD A, E
                CP #8D
                JR NC, @Controls.UnknownE291.PointE4B7                          ; переход, если флаг Carry сброшен


                CP #40
                JR C, @Controls.UnknownE291.PointE4B7                           ; переход, если флаг Carry установлен


                LD E, A
                LD A, C
                AND A
                RRA
                SCF
                RRA
                AND A
                RRA
                XOR C
                AND #F8
                XOR C
                EXX
                LD D, A
                EXX
                LD A, E
                RLCA
                RLCA
                RLCA
                XOR C
                AND #C7
                XOR C
                RLCA
                RLCA
                EXX
                LD E, A
                EXX
                LD A, E
                EXX
                AND #07
                LD C, A
                LD B, #00
                LD HL, #E685
                ADD HL, BC
                LD C, (HL)
                EXX
                LD A, B
                EXX
                SRA A
                SRA A
                JP Z, @Controls.UnknownE291.PointE5E5                           ; переход, если флаг Z установлен


                JP P, @Controls.UnknownE291.PointE5B5                           ; переход, если флаг Sign сброшен


                NEG
                LD B, A
                EXX
                LD A, C
                EXX
                SUB B
                CP #6B
                CCF
                JR C, @Controls.UnknownE291.PointE576                           ; переход, если флаг Carry установлен


                SUB #6B
                ADD A, B
                JP M, @Controls.UnknownE291.PointE5E5                           ; переход, если флаг Sign установлен


                LD B, A
                AND A
                JP Z, @Controls.UnknownE291.PointE5E5                           ; переход, если флаг Z установлен


PointE576:      EX AF, AF'
PointE577:      LD A, (DE)
                OR C
                LD (DE), A
                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE58C                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE58C                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE58C:      DJNZ @Controls.UnknownE291.PointE577

                LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5A0                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE5A0                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE5A0:      LD A, D
                DEC D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5B1                          ; переход, если флаг Z сброшен


                LD A, E
                SUB #20
                LD E, A
                JR C, @Controls.UnknownE291.PointE5B1                           ; переход, если флаг Carry установлен


                LD A, D
                ADD A, #08
                LD D, A
PointE5B1:      LD A, D
                JP @Controls.UnknownE291.PointE5E1


PointE5B5:      LD B, A
                EXX
                LD A, C
                EXX
                ADD A, B
                CP #B5
                JR C, @Controls.UnknownE291.PointE5CA                           ; переход, если флаг Carry установлен


                SUB #B5
                SUB B
                NEG
                LD B, A
                AND A
                JR Z, @Controls.UnknownE291.PointE5E5                           ; переход, если флаг Z установлен


                JP M, @Controls.UnknownE291.PointE5E5                           ; переход, если флаг Sign установлен


PointE5CA:      EX AF, AF'
PointE5CB:      LD A, (DE)
                OR C
                LD (DE), A
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE5DF                          ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Controls.UnknownE291.PointE5DF                           ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
PointE5DF:      DJNZ @Controls.UnknownE291.PointE5CB

PointE5E1:      EX AF, AF'
                JP NC, @Controls.UnknownE291.PointE4B7                          ; переход, если флаг Carry сброшен


PointE5E5:      EXX
                LD A, E
                AND #07
                ADD A, A
                LD E, A
                ADD A, A
                ADD A, E
                EXX
                LD C, A
                LD B, #00
                LD A, (#9C2B)
                INC A
                LD A, (IX + #12)
                JR NZ, @Controls.UnknownE291.PointE5FC                          ; переход, если флаг Z сброшен


                LD A, #01
PointE5FC:      SLA A
                ADD A, #5D
                LD L, A
                LD A, #E6
                ADC A, #00
                LD H, A
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                ADD HL, BC
                PUSH HL
                LD HL, #E68D
                ADD HL, BC
                LD B, (HL)
                INC HL
                LD C, (HL)
                POP HL
                LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                INC HL
                DEC E
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE632                          ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE632                           ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
PointE632:      LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                INC HL
                DEC E
                INC D
                LD A, D
                AND #07
                JP NZ, @Controls.UnknownE291.PointE650                          ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JP C, @Controls.UnknownE291.PointE650                           ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
PointE650:      LD A, (DE)
                AND B
                OR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                AND C
                OR (HL)
                LD (DE), A
                JP @Controls.UnknownE291.PointE4B7


                endmodule
                endmodule
