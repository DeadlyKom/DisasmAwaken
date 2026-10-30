                module Action
                module EdgeCase49
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #49
; исходная запись 17, файловые смещения #61DC..#61F0
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
PointC1DF:      CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC6A9.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC540.Entry
                CALL @Action.UnknownC477.Entry
                JP @Action.EdgeCase09.PointC0B5


                endmodule
                endmodule
