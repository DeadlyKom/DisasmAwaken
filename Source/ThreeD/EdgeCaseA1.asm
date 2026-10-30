                module ThreeD
                module EdgeCaseA1
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #A1
; исходная запись 19, файловые смещения #0412..#0430
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
                JP M, @ThreeD.EdgeCaseA1.PointC42B                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 3, (HL)
                SET 3, (HL)
                CALL NZ, @ThreeD.UnknownC641.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase81.PointC317


PointC42B:      CALL @ThreeD.UnknownC58B.Entry
                JP @ThreeD.EdgeCase01.Entry


                endmodule
                endmodule
