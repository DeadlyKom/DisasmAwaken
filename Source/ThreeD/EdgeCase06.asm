                module ThreeD
                module EdgeCase06
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #06
; исходная запись 19, файловые смещения #0095..#00A3
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
PointC098:      CALL @ThreeD.UnknownC4B5.Entry
PointC09B:      CALL @ThreeD.UnknownC695.Entry
                JP M, @ThreeD.UnknownC58B.Entry                                 ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC540.Entry
                ; JP @ThreeD.EdgeCase46.Entry, продолжение в EdgeCase46.asm

                endmodule
                endmodule
