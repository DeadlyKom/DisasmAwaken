                module ThreeD
                module EdgeCase49
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #49
; исходная запись 19, файловые смещения #01DC..#01F0
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
PointC1DF:      CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC6A9.Entry
                JP M, @ThreeD.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC540.Entry
                CALL @ThreeD.UnknownC477.Entry
                JP @ThreeD.EdgeCase09.PointC0B5


                endmodule
                endmodule
