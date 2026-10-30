                module Action
                module UnknownAC5D
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4C5D..#4CAA
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
Entry:          LD HL, #9BA4
                LD A, (HL)
                LD (#F79C), A
                INC HL
                LD A, (HL)
                INC HL
                LD A, (HL)
                LD (#F798), A
                INC HL
                LD A, (HL)
                LD (#A968), A
                INC HL
                LD A, (HL)
                LD (#63B9), A
                INC HL
                LD A, (HL)
                LD (#A8B5), A
                INC HL
                LD A, (HL)
                LD (#7B6B), A
                LD (#6874), A
                INC HL
                LD A, (HL)
                LD (#6615), A
                INC HL
                LD A, (HL)
                LD (#E6E7), A
                INC HL
                LD A, (HL)
                LD (#E823), A
                INC HL
                LD A, (HL)
                LD (#65E5), A
                INC HL
                LD A, (HL)
                LD (#79A4), A
                INC HL
                LD A, (HL)
                LD (#7E07), A
                INC HL
                LD A, (HL)
                LD (#7E09), A
                INC HL
                LD A, (HL)
                LD (#7DE4), A
                RET


                endmodule
                endmodule
