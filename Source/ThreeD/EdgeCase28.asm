                module ThreeD
                module EdgeCase28
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #28
; исходная запись 19, файловые смещения #017B..#018C
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
PointC17E:      CALL @ThreeD.UnknownC477.Entry
                CALL @ThreeD.UnknownC66D.Entry
                JP P, @ThreeD.UnknownC641.Entry                                 ; переход, если флаг Sign сброшен


                CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.UnknownC4F6.Entry


                endmodule
                endmodule
