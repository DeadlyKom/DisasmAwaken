                module Action
                module EdgeCase06
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #06
; исходная запись 17, файловые смещения #6095..#60A3
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
PointC098:      CALL @Action.UnknownC4B5.Entry
PointC09B:      CALL @Action.UnknownC695.Entry
                JP M, @Action.UnknownC58B.Entry                                 ; переход, если флаг Sign установлен


                CALL @Action.UnknownC540.Entry
                ; JP @Action.EdgeCase46.Entry, продолжение в EdgeCase46.asm

                endmodule
                endmodule
