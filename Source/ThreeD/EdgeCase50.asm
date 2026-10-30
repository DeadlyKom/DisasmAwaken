                module ThreeD
                module EdgeCase50
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #50
; исходная запись 19, файловые смещения #020C..#0227
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
                JP M, @ThreeD.EdgeCase90.PointC38B                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @ThreeD.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
PointC222:      CALL @ThreeD.UnknownC540.Entry
                JP @ThreeD.EdgeCase00.Entry


                endmodule
                endmodule
