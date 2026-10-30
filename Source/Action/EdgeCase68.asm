                module Action
                module EdgeCase68
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #68
; исходная запись 17, файловые смещения #62D0..#62EE
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
                JP M, @Action.EdgeCase68.PointC2E9                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 1, (HL)
                SET 1, (HL)
                CALL NZ, @Action.UnknownC657.Entry                              ; вызов, если флаг Z сброшен
                JP @Action.EdgeCase28.PointC17E


PointC2E9:      CALL @Action.UnknownC540.Entry
                JP @Action.EdgeCase08.Entry


                endmodule
                endmodule
