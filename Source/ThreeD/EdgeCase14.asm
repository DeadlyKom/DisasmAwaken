                module ThreeD
                module EdgeCase14
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #14
; исходная запись 19, файловые смещения #00EF..#0100
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
PointC0F2:      CALL @ThreeD.UnknownC496.Entry
                CALL @ThreeD.UnknownC6A9.Entry
                JP P, @ThreeD.UnknownC662.Entry                                 ; переход, если флаг Sign сброшен


                CALL @ThreeD.UnknownC5E7.Entry
                JP @ThreeD.UnknownC540.Entry


                endmodule
                endmodule
