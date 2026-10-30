                module Action
                module EdgeCase42
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #42
; исходная запись 17, файловые смещения #61BD..#61CE
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
Entry:          CALL @Action.UnknownC496.Entry
PointC1C0:      CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC695.Entry
                JP P, @Action.UnknownC657.Entry                                 ; переход, если флаг Sign сброшен


                CALL @Action.UnknownC540.Entry
                JP @Action.UnknownC58B.Entry


                endmodule
                endmodule
