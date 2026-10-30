                module Action
                module UnknownAACC
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4ACC..#4AE1
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
Entry:          LD L, A
                LD H, #9E
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                LD A, #14
                CALL @Action.SelectMemoryPage.Entry
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                RET


                endmodule
                endmodule
