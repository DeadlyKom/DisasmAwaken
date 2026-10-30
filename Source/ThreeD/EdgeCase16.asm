                module ThreeD
                module EdgeCase16
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #16
; исходная запись 19, файловые смещения #0101..#0118
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
Entry:          CALL @ThreeD.UnknownC4D4.Entry
PointC104:      CALL @ThreeD.UnknownC496.Entry
                CALL @ThreeD.UnknownC6A9.Entry
                JP M, @ThreeD.EdgeCase16.PointC113                              ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC662.Entry
                JP @ThreeD.EdgeCase46.Entry


PointC113:      CALL @ThreeD.UnknownC5E7.Entry
                JP @ThreeD.EdgeCase06.PointC098


                endmodule
                endmodule
