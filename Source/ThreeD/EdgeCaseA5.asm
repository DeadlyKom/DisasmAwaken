                module ThreeD
                module EdgeCaseA5
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #A5
; исходная запись 19, файловые смещения #044D..#0465
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
                CALL @ThreeD.UnknownC4B5.Entry
                CALL @ThreeD.UnknownC66D.Entry
                JP M, @ThreeD.EdgeCase25.PointC165                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 3, (HL)
                SET 3, (HL)
                CALL NZ, @ThreeD.UnknownC641.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase85.PointC341


                endmodule
                endmodule
