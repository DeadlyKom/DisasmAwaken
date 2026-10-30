                module Action
                module EdgeCase25
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #25
; исходная запись 17, файловые смещения #6162..#6173
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
Entry:          CALL @Action.UnknownC4B5.Entry
PointC165:      CALL @Action.UnknownC496.Entry
                CALL @Action.UnknownC695.Entry
                JP M, @Action.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @Action.UnknownC58B.Entry
                JP @Action.EdgeCase05.PointC07E


                endmodule
                endmodule
