                module Action
                module EdgeCase5A
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #5A
; исходная запись 17, файловые смещения #6274..#628C
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
                JP M, @Action.EdgeCase1A.PointC135                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @Action.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
                JP @Action.EdgeCase4A.PointC1F4


                endmodule
                endmodule
