                module ThreeD
                module EdgeCase42
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #42
; исходная запись 19, файловые смещения #01BD..#01CE
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
PointC1C0:      CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC695.Entry
                JP P, @ThreeD.UnknownC657.Entry                                 ; переход, если флаг Sign сброшен


                CALL @ThreeD.UnknownC540.Entry
                JP @ThreeD.UnknownC58B.Entry


                endmodule
                endmodule
