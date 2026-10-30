                module Action
                module EdgeCase69
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #69
; исходная запись 17, файловые смещения #62EF..#6307
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
                JP M, @Action.EdgeCase49.PointC1DF                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 1, (HL)
                SET 1, (HL)
                CALL NZ, @Action.UnknownC657.Entry                              ; вызов, если флаг Z сброшен
                JP @Action.EdgeCase29.PointC190


                endmodule
                endmodule
