                module Action
                module EdgeCase90
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #90
; исходная запись 17, файловые смещения #6375..#6390
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
                CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC681.Entry
                JP M, @Action.EdgeCaseA0.PointC40C                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 2, (HL)
                SET 2, (HL)
                CALL NZ, @Action.UnknownC64C.Entry                              ; вызов, если флаг Z сброшен
PointC38B:      CALL @Action.UnknownC5E7.Entry
                JP @Action.EdgeCase00.Entry


                endmodule
                endmodule
