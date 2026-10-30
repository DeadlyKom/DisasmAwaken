                module Action
                module EdgeCase09
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #09
; исходная запись 17, файловые смещения #60AF..#60BD
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
PointC0B2:      CALL @Action.UnknownC4D4.Entry
PointC0B5:      CALL @Action.UnknownC681.Entry
                JP M, @Action.UnknownC5E7.Entry                                 ; переход, если флаг Sign установлен


                CALL @Action.UnknownC4F6.Entry
                ; JP @Action.EdgeCase89.Entry, продолжение в EdgeCase89.asm

                endmodule
                endmodule
