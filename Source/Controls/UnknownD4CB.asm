                module Controls
                module UnknownD4CB
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #14CB..#14E3
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
Entry:          CALL @Controls.UnknownD504.Entry
                LD A, (#D183)
                LD C, A
                LD A, #80
                ADD A, B
                SUB D
                CALL @Controls.UnknownD515.Entry
                LD A, (#D18C)
                AND A
                LD A, E
                OR #1F
                LD L, A
                LD C, #FF
                RET


                endmodule
                endmodule
