                module Action
                module EdgeCase61
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #61
; исходная запись 17, файловые смещения #62A9..#62BD
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
                CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC695.Entry
                JP M, @Action.EdgeCase41.PointC1AE                              ; переход, если флаг Sign установлен


                CALL @Action.EdgeCase62.Entry
                CALL @Action.UnknownC58B.Entry
                JP @Action.EdgeCase01.Entry


                endmodule
                endmodule
