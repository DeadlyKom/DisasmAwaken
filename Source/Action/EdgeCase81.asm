                module Action
                module EdgeCase81
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #81
; исходная запись 17, файловые смещения #6314..#6325
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
PointC317:      CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC681.Entry
                JP P, @Action.UnknownC64C.Entry                                 ; переход, если флаг Sign сброшен


                CALL @Action.UnknownC4F6.Entry
                JP @Action.UnknownC5E7.Entry


                endmodule
                endmodule
