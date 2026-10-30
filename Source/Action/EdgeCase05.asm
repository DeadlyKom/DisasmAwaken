                module Action
                module EdgeCase05
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #05
; исходная запись 17, файловые смещения #607B..#6089
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
PointC07E:      CALL @Action.UnknownC4D4.Entry
PointC081:      CALL @Action.UnknownC6A9.Entry
                JP M, @Action.UnknownC540.Entry                                 ; переход, если флаг Sign установлен


                CALL @Action.UnknownC5E7.Entry
                ; JP @Action.EdgeCase15.Entry, продолжение в EdgeCase15.asm

                endmodule
                endmodule
