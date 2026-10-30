                module Action
                module Unknown6B16
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0D53..#0E3B
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
                LD (#9B87), A
                LD (#9B88), A
                LD (#9B89), A
                LD A, (#688B)
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                LD B, A
                CALL @Action.Unknown6986.Entry
                LD A, (#9BCA)
                JR Z, @Action.Unknown6B16.Point6B31                             ; переход, если флаг Z установлен


                LD A, #FE
Point6B31:      INC A
                LD C, A
                PUSH IY
                LD IY, #9B27
                LD DE, #000C
Point6B3C:      CALL @Action.Unknown6A29.Entry
                JR NC, @Action.Unknown6B16.Point6B6B                            ; переход, если флаг Carry сброшен


                PUSH DE
                PUSH IY
                PUSH BC
                CALL @Action.Unknown6BFF.Entry
                CALL @Action.Unknown6C7E.Entry
Point6B4B:      POP BC
                POP IY
                POP DE
                DEC C
                JR NZ, @Action.Unknown6B16.Point6B64                            ; переход, если флаг Z сброшен


                LD A, (#D9B7)
                LD (#9B87), A
                LD A, (#D7C5)
                LD (#9B88), A
                LD A, (#D7A3)
                LD (#9B89), A
Point6B64:      ADD IY, DE
                DJNZ @Action.Unknown6B16.Point6B3C

                POP IY
                RET


Point6B6B:      PUSH DE
                PUSH IY
                PUSH BC
                LD B, (IY + #03)
                LD H, (IY + #02)
                LD L, (IY + #01)
                LD A, (IY + #00)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (#9B1E), A
                LD (#9B1F), HL
                LD B, (IY + #07)
                LD H, (IY + #06)
                LD L, (IY + #05)
                LD A, (IY + #04)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (#9B21), A
                LD (#9B22), HL
                LD B, (IY + #0B)
                LD H, (IY + #0A)
                LD L, (IY + #09)
                LD A, (IY + #08)
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                SRA B
                RR H
                RR L
                RRA
                LD (#9B24), A
                LD (#9B25), HL
                CALL @Action.Unknown6C19.Entry
                JP @Action.Unknown6B16.Point6B4B


                endmodule
                endmodule
