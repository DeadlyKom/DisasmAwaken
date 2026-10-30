                module ThreeD
                module EdgeCase05
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #05
; исходная запись 19, файловые смещения #007B..#0089
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
PointC07E:      CALL @ThreeD.UnknownC4D4.Entry
PointC081:      CALL @ThreeD.UnknownC6A9.Entry
                JP M, @ThreeD.UnknownC540.Entry                                 ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC5E7.Entry
                ; JP @ThreeD.EdgeCase15.Entry, продолжение в EdgeCase15.asm

                endmodule
                endmodule
