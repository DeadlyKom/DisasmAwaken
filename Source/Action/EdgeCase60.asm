                module Action
                module EdgeCase60
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #60
; исходная запись 17, файловые смещения #628D..#62A8
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
                CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC695.Entry
                JP M, @Action.EdgeCase50.PointC222                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 1, (HL)
                SET 1, (HL)
                CALL NZ, @Action.UnknownC657.Entry                              ; вызов, если флаг Z сброшен
PointC2A3:      CALL @Action.UnknownC58B.Entry
                JP @Action.EdgeCase00.Entry


                endmodule
                endmodule
