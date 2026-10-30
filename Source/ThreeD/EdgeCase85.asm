                module ThreeD
                module EdgeCase85
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #85
; исходная запись 19, файловые смещения #033E..#0358
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
PointC341:      CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC681.Entry
                JP M, @ThreeD.EdgeCase85.PointC350                              ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC64C.Entry
                JP @ThreeD.EdgeCase15.Entry


PointC350:      CALL @ThreeD.UnknownC4F6.Entry
                CALL @ThreeD.UnknownC496.Entry
                JP @ThreeD.EdgeCase05.PointC081


                endmodule
                endmodule
