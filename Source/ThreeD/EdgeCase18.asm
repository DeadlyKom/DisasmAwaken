                module ThreeD
                module EdgeCase18
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #18
; исходная запись 19, файловые смещения #0119..#012A
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
PointC11C:      CALL @ThreeD.UnknownC477.Entry
                CALL @ThreeD.UnknownC681.Entry
                JP M, @ThreeD.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC5E7.Entry
                JP @ThreeD.UnknownC4F6.Entry


                endmodule
                endmodule
