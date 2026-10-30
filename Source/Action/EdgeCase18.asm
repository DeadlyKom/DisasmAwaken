                module Action
                module EdgeCase18
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #18
; исходная запись 17, файловые смещения #6119..#612A
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
PointC11C:      CALL @Action.UnknownC477.Entry
                CALL @Action.UnknownC681.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC5E7.Entry
                JP @Action.UnknownC4F6.Entry


                endmodule
                endmodule
