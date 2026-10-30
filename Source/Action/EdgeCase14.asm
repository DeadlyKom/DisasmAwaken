                module Action
                module EdgeCase14
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #14
; исходная запись 17, файловые смещения #60EF..#6100
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
Entry:          CALL @Action.UnknownC4D4.Entry
PointC0F2:      CALL @Action.UnknownC496.Entry
                CALL @Action.UnknownC6A9.Entry
                JP P, @Action.UnknownC662.Entry                                 ; переход, если флаг Sign сброшен


                CALL @Action.UnknownC5E7.Entry
                JP @Action.UnknownC540.Entry


                endmodule
                endmodule
