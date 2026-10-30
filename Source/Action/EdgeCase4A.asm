                module Action
                module EdgeCase4A
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #4A
; исходная запись 17, файловые смещения #61F1..#620B
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
PointC1F4:      CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC695.Entry
                JP M, @Action.EdgeCase4A.PointC203                              ; переход, если флаг Sign установлен


                CALL @Action.UnknownC657.Entry
                JP @Action.EdgeCase2A.Entry


PointC203:      CALL @Action.UnknownC540.Entry
                CALL @Action.UnknownC477.Entry
                JP @Action.EdgeCase0A.PointC0CF


                endmodule
                endmodule
