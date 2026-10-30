                module Action
                module Unknown7B58
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #1D95..#20D9
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
Entry:          LD A, #80
                RRCA
                LD (#7B59), A
                RET NC                                                          ; выход, если флаг Carry сброшен

                NOP
                LD A, #00
                DEC A
                JP P, @Action.Unknown7859.Point79A8                             ; переход, если флаг Sign сброшен


                CALL @Action.UnknownEB72.Entry
                LD A, L
                CP #FD
                JP C, @Action.Unknown7859.Point794B                             ; переход, если флаг Carry установлен


                CALL #E9A1
                RET Z                                                           ; выход, если флаг Z установлен

                PUSH IY
                POP IX
                PUSH HL
                CALL #EBB8
                CALL @Action.Unknown699C.Entry
                LD A, L
                SRL A
                SRL A
                LD D, #99
                LD E, A
                LD A, (DE)
                LD D, A
                RRCA
                RRCA
                RRCA
                RRCA
                AND #07
                LD C, #00
                SUB H
                JR C, @Action.Unknown7B58.Point7B94                             ; переход, если флаг Carry установлен


                XOR A
Point7B94:      NEG
                CP #0A
                LD A, H
                NOP
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #43
                LD C, #01
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #50
                LD C, #02
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #50
                LD C, #03
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #5A
                LD C, #04
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #5E
                LD C, #05
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #63
                LD C, #06
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #6B
                LD C, #07
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                CP #70
                LD C, #08
                JR C, @Action.Unknown7B58.Point7BCE                             ; переход, если флаг Carry установлен


                POP DE
                RET


Point7BCE:      LD A, C
                CP #08
                JR NZ, @Action.Unknown7B58.Point7BDB                            ; переход, если флаг Z сброшен


                LD A, (#9B82)
                OR A
                JR Z, @Action.Unknown7B58.Point7BDB                             ; переход, если флаг Z установлен


                POP DE
                RET


Point7BDB:      LD (IX + #12), C
                SLA C
                LD B, #00
                LD HL, #7AC6
                ADD HL, BC
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                LD A, R
                AND #07
                RLA
                ADD A, L
                LD L, A
                LD A, H
                ADC A, #00
                LD H, A
                LD A, (HL)
                LD (IX + #06), A
                INC HL
                LD L, (HL)
                LD (IX + #0F), L
                LD H, D
                POP DE
                LD L, A
                LD A, (IX + #12)
                CP #06
                JR Z, @Action.Unknown7B58.Point7C21                             ; переход, если флаг Z установлен


                CP #07
                JR Z, @Action.Unknown7B58.Point7C21                             ; переход, если флаг Z установлен


                LD A, #80
                SUB H
                LD H, A
                LD A, #80
                SUB D
                SRL A
                ADD A, #19
                CP H
                JP C, @Action.Unknown7B58.Point7C78                             ; переход, если флаг Carry установлен


                LD A, C
                CP #10
                JP Z, @Action.Unknown7B58.Point7C78                             ; переход, если флаг Z установлен


Point7C21:      LD A, L
                CALL @Action.UnknownAACC.Entry
                LD A, H
                PUSH AF
                CALL #EB80
                SRA H
                RR L
                LD (IX + #04), L
                LD (IX + #05), H
                PUSH HL
                CALL #EB87
                SRA H
                RR L
                LD (IX + #02), L
                LD (IX + #03), H
                PUSH HL
                CALL #EB8E
                SRA H
                RR L
                LD (IX + #00), L
                LD (IX + #01), H
                POP DE
                POP BC
                POP AF
                EX AF, AF'
                LD A, #1A
                EXX
                LD HL, #EC00
                CALL @Action.Unknown6CEF.Entry
                LD A, #01
                LD (#6D39), A
                LD A, (#6D3D)
                CP #1A
                JR NC, @Action.Unknown7B58.Point7C6E                            ; переход, если флаг Carry сброшен


                LD A, #1A
                LD (#6D3D), A
Point7C6E:      LD (IX + #0A), #01
                CALL @Action.Unknown7E9D.Entry
                JP @Action.Unknown7B58.Point7DD4


Point7C78:      LD A, R
                BIT 1, A
                JP Z, @Action.Unknown7B58.Point7CDD                             ; переход, если флаг Z установлен


                CALL #E98D
                LD A, (#9B83)
                AND A
                JP Z, @Action.Unknown7B58.Point7CDD                             ; переход, если флаг Z установлен


                LD A, (IX + #12)
                CP #00
                JP Z, @Action.Unknown7B58.Point7CDD                             ; переход, если флаг Z установлен


                CP #05
                JP NC, @Action.Unknown7B58.Point7CDD                            ; переход, если флаг Carry сброшен


                LD D, #12
                CALL #E98D
                JR Z, @Action.Unknown7B58.Point7CDD                             ; переход, если флаг Z установлен


                LD L, (IY + #00)
                LD H, (IY + #01)
                LD (IX + #00), L
                LD (IX + #01), H
                LD L, (IY + #02)
                LD H, (IY + #03)
                LD A, R
                AND #01
                INC A
                LD D, A
                LD E, #80
                ADD HL, DE
                LD (IX + #02), L
                LD (IX + #03), H
                LD L, (IY + #04)
                LD H, (IY + #05)
                LD (IX + #04), L
                LD (IX + #05), H
                LD (IX + #0A), #01
                LD (IX + #07), #40
                LD (IX + #08), #00
                LD (IX + #09), #00
                JP @Action.Unknown7B58.Point7DD8


Point7CDD:      LD HL, (#9B70)
                LD DE, (#9B73)
                LD BC, (#9B76)
                BIT 7, H
                JR Z, @Action.Unknown7B58.Point7CF3                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point7CF3:      BIT 7, D
                JR Z, @Action.Unknown7B58.Point7CFE                             ; переход, если флаг Z установлен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
Point7CFE:      BIT 7, B
                JR Z, @Action.Unknown7B58.Point7D09                             ; переход, если флаг Z установлен


                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
Point7D09:      SLA L
                RL H
                JP M, @Action.Unknown7B58.Point7D28                             ; переход, если флаг Sign установлен


                SLA E
                RL D
                JP M, @Action.Unknown7B58.Point7D23                             ; переход, если флаг Sign установлен


                SLA C
                RL B
                JP P, @Action.Unknown7B58.Point7D09                             ; переход, если флаг Sign сброшен


                RR B
                RR C
                AND A
Point7D23:      RR D
                RR E
                AND A
Point7D28:      RR H
                RR L
                RES 1, B
                RES 1, D
                RES 1, H
                LD A, (#9B71)
                AND A
                JP P, @Action.Unknown7B58.Point7D40                             ; переход, если флаг Sign сброшен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point7D40:      LD A, (#9B74)
                AND A
                JP P, @Action.Unknown7B58.Point7D4E                             ; переход, если флаг Sign сброшен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
Point7D4E:      LD A, (#9B77)
                AND A
                JP P, @Action.Unknown7B58.Point7D5C                             ; переход, если флаг Sign сброшен


                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
Point7D5C:      PUSH BC
                PUSH DE
                PUSH HL
                CALL #EB80
                LD A, H
                AND #0F
                JR NZ, @Action.Unknown7B58.Point7D69                            ; переход, если флаг Z сброшен


                OR #07
Point7D69:      BIT 7, H
                JR Z, @Action.Unknown7B58.Point7D6E                             ; переход, если флаг Z установлен


                CPL
Point7D6E:      LD H, A
                POP DE
                ADD HL, DE
                LD (IX + #00), L
                LD (IX + #01), H
                CALL #EB87
                LD A, H
                AND #0F
                JR NZ, @Action.Unknown7B58.Point7D81                            ; переход, если флаг Z сброшен


                OR #07
Point7D81:      BIT 7, H
                JR Z, @Action.Unknown7B58.Point7D86                             ; переход, если флаг Z установлен


                CPL
Point7D86:      LD H, A
                POP DE
                ADD HL, DE
                LD (IX + #02), L
                LD (IX + #03), H
                CALL #EB8E
                LD A, H
                AND #03
                JR NZ, @Action.Unknown7B58.Point7D99                            ; переход, если флаг Z сброшен


                OR #01
Point7D99:      BIT 7, H
                JR Z, @Action.Unknown7B58.Point7D9E                             ; переход, если флаг Z установлен


                CPL
Point7D9E:      LD H, A
                POP DE
                ADD HL, DE
                LD (IX + #04), L
                LD (IX + #05), H
                LD (IX + #0A), #01
                CALL #EB8E
                LD A, L
                AND #07
                LD L, A
                LD A, (#688B)
                OR A
                JR Z, @Action.Unknown7B58.Point7DD4                             ; переход, если флаг Z установлен


                LD H, A
                LD A, L
Point7DBA:      CP H
                JR C, @Action.Unknown7B58.Point7DC1                             ; переход, если флаг Carry установлен


                SRL A
                JR @Action.Unknown7B58.Point7DBA


Point7DC1:      LD (IX + #26), A
                LD IY, #9B1B
                LD DE, #000C
                LD B, A
                INC B
Point7DCD:      ADD IY, DE
                DJNZ @Action.Unknown7B58.Point7DCD

                CALL @Action.Unknown7EB7.Entry
Point7DD4:      LD (IX + #07), #00
Point7DD8:      CALL #EBC6
                LD A, L
                AND #55
                LD L, A
                LD A, H
                AND #2A
                AND L
                OR #20
                LD (IX + #11), A
                LD (IX + #0C), #00
                LD (IX + #14), #00
                LD (IX + #15), #FF
                LD (IX + #0B), #FF
                LD HL, (#EBDB)
                LD (IX + #0D), L
                LD (IX + #0E), H
                CALL #EBCD
                LD E, H
                LD A, L
                OR #32
                LD H, #64
                CP H
                JR C, @Action.Unknown7B58.Point7E0F                             ; переход, если флаг Carry установлен


                LD A, H
                DEC A
Point7E0F:      LD (IX + #13), A
                LD A, E
                OR #A0
                LD (IX + #22), A
                LD A, #20
                LD (IX + #10), A
                XOR A
                LD (#EBDD), A
                LD A, (IX + #12)
                CP #08
                JR NZ, @Action.Unknown7B58.Point7E42                            ; переход, если флаг Z сброшен


                LD (IX + #13), #F0
                LD (IX + #22), #FA
                LD A, (IX + #07)
                LD (IX + #0D), A
                LD A, (IX + #08)
                LD (IX + #0E), A
                LD A, (IX + #09)
                LD (IX + #0F), A
Point7E42:      LD A, (IX + #12)
                CP #06
                JR NZ, @Action.Unknown7B58.Point7E5D                            ; переход, если флаг Z сброшен


                CP #07
                JR NZ, @Action.Unknown7B58.Point7E5D                            ; переход, если флаг Z сброшен


                LD (IX + #13), #F0
                LD (IX + #22), #FA
                LD (IX + #11), #6E
                LD (IX + #24), #00
Point7E5D:      LD A, (IX + #0A)
                LD (IX + #16), A
                LD A, R
                AND #0F
                INC A
                AND #0F
                LD C, A
                LD A, (IX + #12)
                CP #08
                JR NZ, @Action.Unknown7B58.Point7E7A                            ; переход, если флаг Z сброшен


                LD A, R
                AND #40
                JR Z, @Action.Unknown7B58.Point7E7A                             ; переход, если флаг Z установлен


                SET 2, C
Point7E7A:      LD (IX + #18), C
                LD (IX + #17), #00
                LD (IX + #20), #FF
                LD (IX + #21), #FF
Point7E89:      LD A, (IX + #06)
                CALL @Action.UnknownAACC.Entry
                LD A, H
                CP #04
                LD A, #02
                JR NZ, @Action.Unknown7B58.Point7E97                            ; переход, если флаг Z сброшен


                DEC A
Point7E97:      LD (IX + #25), A
                JP @Action.Unknown64DF.Entry


                endmodule
                endmodule
