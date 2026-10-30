                module ThreeD
                module EdgeCase25
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #25
; исходная запись 19, файловые смещения #0162..#0173
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
PointC165:      CALL @ThreeD.UnknownC496.Entry
                CALL @ThreeD.UnknownC695.Entry
                JP M, @ThreeD.EdgeCase59.Entry                                  ; переход, если флаг Sign установлен


                CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.EdgeCase05.PointC07E


                endmodule
                endmodule
