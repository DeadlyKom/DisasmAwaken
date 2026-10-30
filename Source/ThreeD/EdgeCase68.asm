                module ThreeD
                module EdgeCase68
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #68
; исходная запись 19, файловые смещения #02D0..#02EE
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
                JP M, @ThreeD.EdgeCase68.PointC2E9                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 1, (HL)
                SET 1, (HL)
                CALL NZ, @ThreeD.UnknownC657.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase28.PointC17E


PointC2E9:      CALL @ThreeD.UnknownC540.Entry
                JP @ThreeD.EdgeCase08.Entry


                endmodule
                endmodule
