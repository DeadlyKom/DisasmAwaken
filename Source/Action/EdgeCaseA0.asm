                module Action
                module EdgeCaseA0
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #A0
; исходная запись 17, файловые смещения #63F6..#6411
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
                CALL @Action.UnknownC4B5.Entry
                CALL @Action.UnknownC66D.Entry
                JP M, @Action.EdgeCase60.PointC2A3                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 3, (HL)
                SET 3, (HL)
                CALL NZ, @Action.UnknownC641.Entry                              ; вызов, если флаг Z сброшен
PointC40C:      CALL @Action.UnknownC4F6.Entry
                JP @Action.EdgeCase00.Entry


                endmodule
                endmodule
