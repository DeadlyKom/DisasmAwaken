                module ThreeD
                module EdgeCase29
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #29
; исходная запись 19, файловые смещения #018D..#01A4
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
Entry:          CALL @ThreeD.UnknownC4B5.Entry
PointC190:      CALL @ThreeD.UnknownC477.Entry
                CALL @ThreeD.UnknownC66D.Entry
                JP M, @ThreeD.EdgeCase29.PointC19F                              ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC641.Entry
                JP @ThreeD.EdgeCase89.Entry


PointC19F:      CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.EdgeCase09.PointC0B2


                endmodule
                endmodule
