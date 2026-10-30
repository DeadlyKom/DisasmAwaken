                module Action
                module EdgeCase41
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #41
; исходная запись 17, файловые смещения #61AB..#61BC
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
PointC1AE:      CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC6A9.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC540.Entry
                JP @Action.UnknownC5E7.Entry


                endmodule
                endmodule
