                module Action
                module EdgeCase92
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #92
; исходная запись 17, файловые смещения #639C..#63B0
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
Entry:          CALL @Action.UnknownC477.Entry
                CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC681.Entry
                JP M, @Action.EdgeCase82.PointC329                              ; переход, если флаг Sign установлен


                CALL @Action.EdgeCase91.Entry
                CALL @Action.UnknownC5E7.Entry
                JP @Action.EdgeCase02.Entry


                endmodule
                endmodule
