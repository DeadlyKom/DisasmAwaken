                module Action
                module UnknownAD48
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4D48..#4D59
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
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UnknownB0E9.Entry
                EX AF, AF'
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                POP BC
                RET


                endmodule
                endmodule
