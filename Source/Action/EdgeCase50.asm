                module Action
                module EdgeCase50
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #50
; исходная запись 17, файловые смещения #620C..#6227
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
                CALL @Action.UnknownC4D4.Entry
                CALL @Action.UnknownC6A9.Entry
                JP M, @Action.EdgeCase90.PointC38B                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @Action.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
PointC222:      CALL @Action.UnknownC540.Entry
                JP @Action.EdgeCase00.Entry


                endmodule
                endmodule
