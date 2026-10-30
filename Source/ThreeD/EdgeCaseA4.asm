                module ThreeD
                module EdgeCaseA4
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #A4
; исходная запись 19, файловые смещения #0438..#044C
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
Entry:          CALL @ThreeD.UnknownC477.Entry
                CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC66D.Entry
                JP M, @ThreeD.EdgeCase24.PointC153                              ; переход, если флаг Sign установлен


                CALL @ThreeD.EdgeCaseA8.Entry
                CALL @ThreeD.UnknownC4F6.Entry
                JP @ThreeD.EdgeCase04.Entry


                endmodule
                endmodule
