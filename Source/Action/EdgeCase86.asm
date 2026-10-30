                module Action
                module EdgeCase86
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #86
; исходная запись 17, файловые смещения #6359..#636D
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
PointC35C:      CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC66D.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC4F6.Entry
                CALL @Action.UnknownC496.Entry
                JP @Action.EdgeCase06.PointC09B


                endmodule
                endmodule
