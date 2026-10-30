                module Action
                module EdgeCase96
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #96
; исходная запись 17, файловые смещения #63D6..#63EE
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
                JP M, @Action.EdgeCase86.PointC35C                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 2, (HL)
                SET 2, (HL)
                CALL NZ, @Action.UnknownC64C.Entry                              ; вызов, если флаг Z сброшен
                JP @Action.EdgeCase16.PointC104


                endmodule
                endmodule
