                module Action
                module EdgeCase0A
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #0A
; исходная запись 17, файловые смещения #60C9..#60D7
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
PointC0CC:      CALL @Action.UnknownC4B5.Entry
PointC0CF:      CALL @Action.UnknownC66D.Entry
                JP M, @Action.UnknownC4F6.Entry                                 ; переход, если флаг Sign установлен


                CALL @Action.UnknownC58B.Entry
                ; JP @Action.EdgeCase2A.Entry, продолжение в EdgeCase2A.asm

                endmodule
                endmodule
