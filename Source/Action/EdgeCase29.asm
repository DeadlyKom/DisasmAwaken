                module Action
                module EdgeCase29
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #29
; исходная запись 17, файловые смещения #618D..#61A4
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
Entry:          CALL @Action.UnknownC4B5.Entry
PointC190:      CALL @Action.UnknownC477.Entry
                CALL @Action.UnknownC66D.Entry
                JP M, @Action.EdgeCase29.PointC19F                              ; переход, если флаг Sign установлен


                CALL @Action.UnknownC641.Entry
                JP @Action.EdgeCase89.Entry


PointC19F:      CALL @Action.UnknownC58B.Entry
                JP @Action.EdgeCase09.PointC0B2


                endmodule
                endmodule
