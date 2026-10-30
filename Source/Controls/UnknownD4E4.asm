                module Controls
                module UnknownD4E4
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #14E4..#1500
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
                ADD A, D
                SUB B
                CALL @Controls.UnknownD53C.Entry
                LD A, L
                AND #E0
                OR #01
                LD E, A
                LD B, A
                LD A, (#D18C)
                AND A
                LD A, B
                LD B, #00
                RET


                endmodule
                endmodule
