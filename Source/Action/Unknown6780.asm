                module Action
                module Unknown6780
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #09BD..#0BB9
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
Entry:          LD HL, #8000
                SRL H
                RR L
                LD (#6781), HL
                JP NC, @Action.Unknown6780.Point688A                            ; переход, если флаг Carry сброшен


                RR H
                LD (#6781), HL
                LD A, (#9B81)
                DEC A
                JR Z, @Action.Unknown66D2.Point6742                             ; переход, если флаг Z установлен


                DEC A
                JR Z, @Action.Unknown66D2.Point6765                             ; переход, если флаг Z установлен


Point679B:      LD HL, (#9B6F)
                LD A, (#9B71)
                LD DE, (#E5B3)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown6780.Point67AC                             ; переход, если флаг Z установлен


                DEC C
Point67AC:      OR A
                SBC HL, DE
                LD (#9B6F), HL
                SBC A, C
                JP PE, @Action.Unknown66D2.Point6727                            ; переход, если флаг P/V установлен


                LD (#9B71), A
                LD HL, (#9B72)
                LD A, (#9B74)
                LD DE, (#E5D2)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown6780.Point67CA                             ; переход, если флаг Z установлен


                DEC C
Point67CA:      OR A
                SBC HL, DE
                LD (#9B72), HL
                SBC A, C
                JP PE, @Action.Unknown66D2.Point6727                            ; переход, если флаг P/V установлен


                LD (#9B74), A
                LD HL, (#9B75)
                LD DE, (#E5ED)
                LD A, (#9B77)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown6780.Point67E8                             ; переход, если флаг Z установлен


                DEC C
Point67E8:      OR A
                SBC HL, DE
                LD (#9B75), HL
                SBC A, C
                JP PE, @Action.Unknown66D2.Point6727                            ; переход, если флаг P/V установлен


                LD (#9B77), A
                CALL @Action.Unknown699C.Entry
                LD A, L
                AND A
                JR NZ, @Action.Unknown6780.Point685F                            ; переход, если флаг Z сброшен


                LD HL, (#9B70)
                BIT 7, H
                LD A, L
                JR Z, @Action.Unknown6780.Point6806                             ; переход, если флаг Z установлен


                NEG
Point6806:      LD E, A
                LD HL, (#9B73)
                BIT 7, H
                LD A, L
                JR Z, @Action.Unknown6780.Point6811                             ; переход, если флаг Z установлен


                NEG
Point6811:      CP E
                JR C, @Action.Unknown6780.Point6815                             ; переход, если флаг Carry установлен


                LD E, A
Point6815:      LD HL, (#9B76)
                BIT 7, H
                LD A, L
                JR Z, @Action.Unknown6780.Point681F                             ; переход, если флаг Z установлен


                NEG
Point681F:      CP E
                JR C, @Action.Unknown6780.Point6823                             ; переход, если флаг Carry установлен


                LD E, A
Point6823:      LD A, E
                NEG
                SRL A
                CP #2F
                JR C, @Action.Unknown6780.Point682E                             ; переход, если флаг Carry установлен


                LD A, #2E
Point682E:      LD (#6682), A
                LD A, #01
                LD (#667D), A
                LD A, (#9C29)
                INC A
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, #80
                RRCA
                LD (#683C), A
                JP NC, @Action.Unknown6780.Point688A                            ; переход, если флаг Carry сброшен


                CALL @Action.Unknown74FB.Entry
                INC A
                LD C, A
                LD DE, (#9BD2)
                INC E
                LD A, D
                CP E
                JR C, @Action.Unknown6780.Point6857                             ; переход, если флаг Carry установлен


                LD (#9BD2), DE
                LD (HL), C
Point6857:      LD A, #01
                LD (#665C), A
                JP @Action.Unknown6780.Point688A


Point685F:      LD A, (#6682)
                AND A
                JR Z, @Action.Unknown6780.Point686C                             ; переход, если флаг Z установлен


                LD (#667D), A
                XOR A
                LD (#6682), A
Point686C:      LD A, L
                CP #1C
                JR C, @Action.Unknown6780.Point687C                             ; переход, если флаг Carry установлен


                SUB #1B
                ADD A, #00
                JR NC, @Action.Unknown6780.Point6879                            ; переход, если флаг Carry сброшен


                LD A, #FF
Point6879:      LD (#7B6B), A
Point687C:      LD A, L
                CP #40
                JP C, @Action.Unknown6780.Point688A                             ; переход, если флаг Carry установлен


                LD A, (#9B81)
                CP #02
                JP NZ, @Action.Unknown66D2.Point6727                            ; переход, если флаг Z сброшен


Point688A:      LD A, #00
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                PUSH AF
                LD HL, (#E5B3)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.Unknown6780.Point689F                            ; переход, если флаг Z сброшен


                INC L
Point689F:      LD (#68D5), HL
                LD HL, (#E5D2)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.Unknown6780.Point68B2                            ; переход, если флаг Z сброшен


                INC L
Point68B2:      LD (#68FD), HL
                LD HL, (#E5ED)
                SRA H
                RR L
                SRA H
                RR L
                LD A, H
                OR L
                JR NZ, @Action.Unknown6780.Point68C5                            ; переход, если флаг Z сброшен


                INC L
Point68C5:      LD (#6925), HL
                POP AF
                LD IY, #9B27
Point68CD:      EX AF, AF'
                LD L, (IY + #00)
                LD H, (IY + #01)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.Unknown6780.Point68DF                             ; переход, если флаг Z установлен


                DEC BC
Point68DF:      OR A
                SBC HL, DE
                LD (IY + #00), L
                LD (IY + #01), H
                LD L, (IY + #02)
                LD H, (IY + #03)
                SBC HL, BC
                LD (IY + #02), L
                LD (IY + #03), H
                LD L, (IY + #04)
                LD H, (IY + #05)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.Unknown6780.Point6907                             ; переход, если флаг Z установлен


                DEC BC
Point6907:      OR A
                SBC HL, DE
                LD (IY + #04), L
                LD (IY + #05), H
                LD L, (IY + #06)
                LD H, (IY + #07)
                SBC HL, BC
                LD (IY + #06), L
                LD (IY + #07), H
                LD L, (IY + #08)
                LD H, (IY + #09)
                LD DE, #0000
                BIT 7, D
                LD BC, #0000
                JR Z, @Action.Unknown6780.Point692F                             ; переход, если флаг Z установлен


                DEC BC
Point692F:      OR A
                SBC HL, DE
                LD (IY + #08), L
                LD (IY + #09), H
                LD L, (IY + #0A)
                LD H, (IY + #0B)
                SBC HL, BC
                LD (IY + #0A), L
                LD (IY + #0B), H
                LD BC, #000C
                ADD IY, BC
                EX AF, AF'
                DEC A
                JP NZ, @Action.Unknown6780.Point68CD                            ; переход, если флаг Z сброшен


                CALL @Action.Unknown69BE.Entry
                LD A, L
                AND A
                JR NZ, @Action.Unknown6780.Point696B                            ; переход, если флаг Z сброшен


                LD A, H
                NEG
                SRL A
                CP #2F
                JR C, @Action.Unknown6780.Point6962                             ; переход, если флаг Carry установлен


                LD A, #2E
Point6962:      LD (#6693), A
                LD A, #01
                LD (#668E), A
                RET


Point696B:      LD A, (#6693)
                AND A
                JR Z, @Action.Unknown6780.Point6978                             ; переход, если флаг Z установлен


                LD (#668E), A
                XOR A
                LD (#6693), A
Point6978:      LD A, (#9BC5)
                CP E
                RET


                endmodule
                endmodule
