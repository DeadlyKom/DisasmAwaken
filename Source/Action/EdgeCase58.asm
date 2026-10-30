                module Action
                module EdgeCase58
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #58
; исходная запись 17, файловые смещения #625F..#6273
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
                CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC6A9.Entry
                JP M, @Action.EdgeCase18.PointC11C                              ; переход, если флаг Sign установлен


                CALL @Action.EdgeCase54.Entry
                CALL @Action.UnknownC540.Entry
                JP @Action.EdgeCase08.Entry


                endmodule
                endmodule
