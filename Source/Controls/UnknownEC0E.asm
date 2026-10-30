                module Controls
                module UnknownEC0E
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #1130..#1177
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
Entry:          LD HL, #0000
                LD (#ECA3), HL
                LD HL, #EC7E
                LD (#ECAA), HL
                INC HL
                INC HL
                LD (#EC5D), HL
                LD IX, #ED19
                LD BC, #0014
                LD HL, #5074
                LD DE, #5060
                LD A, #1E
PointEC2E:      ADD IX, BC
                LD (IX + #00), L
                LD (IX + #01), H
                LD (IX + #0A), E
                LD (IX + #0B), D
                EX AF, AF'
                INC H
                INC D
                LD A, H
                AND #07
                CP #06
                JR NZ, @Controls.UnknownEC0E.PointEC51                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                LD A, E
                ADD A, #20
                LD E, A
                LD H, #50
                LD D, H
PointEC51:      EX AF, AF'
                DEC A
                JR NZ, @Controls.UnknownEC0E.PointEC2E                          ; переход, если флаг Z сброшен


                RET


                endmodule
                endmodule
