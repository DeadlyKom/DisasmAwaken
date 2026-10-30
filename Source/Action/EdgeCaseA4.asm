                module Action
                module EdgeCaseA4
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #A4
; исходная запись 17, файловые смещения #6438..#644C
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
                CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC66D.Entry
                JP M, @Action.EdgeCase24.PointC153                              ; переход, если флаг Sign установлен


                CALL @Action.EdgeCaseA8.Entry
                CALL @Action.UnknownC4F6.Entry
                JP @Action.EdgeCase04.Entry


                endmodule
                endmodule
