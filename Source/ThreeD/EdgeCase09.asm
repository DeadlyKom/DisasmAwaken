                module ThreeD
                module EdgeCase09
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #09
; исходная запись 19, файловые смещения #00AF..#00BD
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
PointC0B2:      CALL @ThreeD.UnknownC4D4.Entry
PointC0B5:      CALL @ThreeD.UnknownC681.Entry
                JP M, @ThreeD.UnknownC5E7.Entry                                 ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC4F6.Entry
                ; JP @ThreeD.EdgeCase89.Entry, продолжение в EdgeCase89.asm

                endmodule
                endmodule
