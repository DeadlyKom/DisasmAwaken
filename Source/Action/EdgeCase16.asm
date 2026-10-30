                module Action
                module EdgeCase16
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #16
; исходная запись 17, файловые смещения #6101..#6118
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
PointC104:      CALL @Action.UnknownC496.Entry
                CALL @Action.UnknownC6A9.Entry
                JP M, @Action.EdgeCase16.PointC113                              ; переход, если флаг Sign установлен


                CALL @Action.UnknownC662.Entry
                JP @Action.EdgeCase46.Entry


PointC113:      CALL @Action.UnknownC5E7.Entry
                JP @Action.EdgeCase06.PointC098


                endmodule
                endmodule
