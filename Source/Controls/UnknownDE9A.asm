                module Controls
                module UnknownDE9A
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #03BC..#03FD
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
Entry:          PUSH BC
                EX AF, AF'
                LD A, H
                XOR L
                XOR E
                XOR D
                AND #07
                DEC A
                JP P, @Controls.UnknownDE9A.PointDEA7                           ; переход, если флаг Sign сброшен


                XOR A
PointDEA7:      EX AF, AF'
                LD (#9B15), HL
                LD (#9B17), DE
                INC A
                LD B, A
                CALL #6E2B
                LD C, A
                LD A, C
                CP #03
                LD C, #00
                JR NZ, @Controls.UnknownDE9A.PointDEBD                          ; переход, если флаг Z сброшен


                INC C
PointDEBD:      CALL @Controls.UnknownDD5D.Entry
                DJNZ @Controls.UnknownDE9A.PointDEBD

                CPL
                LD E, A
                AND #3C
                RRCA
                RRCA
                INC A
                LD L, A
                LD A, E
                RLCA
                RLCA
                AND #03
                DEC C
                JR NZ, @Controls.UnknownDE9A.PointDED4                          ; переход, если флаг Z сброшен


                LD A, #04
PointDED4:      LD H, A
                LD A, E
                AND #03
                LD E, A
                EX AF, AF'
                POP BC
                RET


                endmodule
                endmodule
