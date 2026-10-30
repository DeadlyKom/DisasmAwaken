                module ThreeD
                module EdgeCase92
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #92
; исходная запись 19, файловые смещения #039C..#03B0
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
                CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC681.Entry
                JP M, @ThreeD.EdgeCase82.PointC329                              ; переход, если флаг Sign установлен


                CALL @ThreeD.EdgeCase91.Entry
                CALL @ThreeD.UnknownC5E7.Entry
                JP @ThreeD.EdgeCase02.Entry


                endmodule
                endmodule
