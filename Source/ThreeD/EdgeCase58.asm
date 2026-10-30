                module ThreeD
                module EdgeCase58
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #58
; исходная запись 19, файловые смещения #025F..#0273
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
                CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC6A9.Entry
                JP M, @ThreeD.EdgeCase18.PointC11C                              ; переход, если флаг Sign установлен


                CALL @ThreeD.EdgeCase54.Entry
                CALL @ThreeD.UnknownC540.Entry
                JP @ThreeD.EdgeCase08.Entry


                endmodule
                endmodule
