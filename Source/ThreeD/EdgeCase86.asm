                module ThreeD
                module EdgeCase86
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #86
; исходная запись 19, файловые смещения #0359..#036D
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
PointC35C:      CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC66D.Entry
                JP M, @ThreeD.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC4F6.Entry
                CALL @ThreeD.UnknownC496.Entry
                JP @ThreeD.EdgeCase06.PointC09B


                endmodule
                endmodule
