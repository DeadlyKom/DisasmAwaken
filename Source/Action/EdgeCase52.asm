                module Action
                module EdgeCase52
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #52
; исходная запись 17, файловые смещения #622F..#624D
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
                JP M, @Action.EdgeCase52.PointC248                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @Action.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
                JP @Action.EdgeCase42.PointC1C0


PointC248:      CALL @Action.UnknownC5E7.Entry
                JP @Action.EdgeCase02.Entry


                endmodule
                endmodule
