                module ThreeD
                module EdgeCase61
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #61
; исходная запись 19, файловые смещения #02A9..#02BD
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
Entry:          CALL @ThreeD.UnknownC496.Entry
                CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC695.Entry
                JP M, @ThreeD.EdgeCase41.PointC1AE                              ; переход, если флаг Sign установлен


                CALL @ThreeD.EdgeCase62.Entry
                CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.EdgeCase01.Entry


                endmodule
                endmodule
