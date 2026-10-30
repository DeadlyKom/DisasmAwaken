                module ThreeD
                module EdgeCase4A
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #4A
; исходная запись 19, файловые смещения #01F1..#020B
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
PointC1F4:      CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC695.Entry
                JP M, @ThreeD.EdgeCase4A.PointC203                              ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC657.Entry
                JP @ThreeD.EdgeCase2A.Entry


PointC203:      CALL @ThreeD.UnknownC540.Entry
                CALL @ThreeD.UnknownC477.Entry
                JP @ThreeD.EdgeCase0A.PointC0CF


                endmodule
                endmodule
