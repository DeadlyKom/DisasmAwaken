                module ThreeD
                module EdgeCase0A
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #0A
; исходная запись 19, файловые смещения #00C9..#00D7
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
PointC0CC:      CALL @ThreeD.UnknownC4B5.Entry
PointC0CF:      CALL @ThreeD.UnknownC66D.Entry
                JP M, @ThreeD.UnknownC4F6.Entry                                 ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC58B.Entry
                ; JP @ThreeD.EdgeCase2A.Entry, продолжение в EdgeCase2A.asm

                endmodule
                endmodule
