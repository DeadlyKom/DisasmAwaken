                module ThreeD
                module EdgeCase60
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #60
; исходная запись 19, файловые смещения #028D..#02A8
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
                CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC695.Entry
                JP M, @ThreeD.EdgeCase50.PointC222                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 1, (HL)
                SET 1, (HL)
                CALL NZ, @ThreeD.UnknownC657.Entry                              ; вызов, если флаг Z сброшен
PointC2A3:      CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.EdgeCase00.Entry


                endmodule
                endmodule
