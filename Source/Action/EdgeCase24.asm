                module Action
                module EdgeCase24
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #24
; исходная запись 17, файловые смещения #6150..#6161
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
PointC153:      CALL @Action.UnknownC496.Entry
                CALL @Action.UnknownC695.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC58B.Entry
                JP @Action.UnknownC540.Entry


                endmodule
                endmodule
