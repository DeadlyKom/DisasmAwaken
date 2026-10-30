                module ThreeD
                module EdgeCase81
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #81
; исходная запись 19, файловые смещения #0314..#0325
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
PointC317:      CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC681.Entry
                JP P, @ThreeD.UnknownC64C.Entry                                 ; переход, если флаг Sign сброшен


                CALL @ThreeD.UnknownC4F6.Entry
                JP @ThreeD.UnknownC5E7.Entry


                endmodule
                endmodule
