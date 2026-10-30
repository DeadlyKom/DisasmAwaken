                module Action
                module EdgeCase85
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #85
; исходная запись 17, файловые смещения #633E..#6358
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
PointC341:      CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC681.Entry
                JP M, @Action.EdgeCase85.PointC350                              ; переход, если флаг Sign установлен


                CALL @Action.UnknownC64C.Entry
                JP @Action.EdgeCase15.Entry


PointC350:      CALL @Action.UnknownC4F6.Entry
                CALL @Action.UnknownC496.Entry
                JP @Action.EdgeCase05.PointC081


                endmodule
                endmodule
