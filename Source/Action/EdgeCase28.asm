                module Action
                module EdgeCase28
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #28
; исходная запись 17, файловые смещения #617B..#618C
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
PointC17E:      CALL @Action.UnknownC477.Entry
                CALL @Action.UnknownC66D.Entry
                JP P, @Action.UnknownC641.Entry                                 ; переход, если флаг Sign сброшен


                CALL @Action.UnknownC58B.Entry
                JP @Action.UnknownC4F6.Entry


                endmodule
                endmodule
