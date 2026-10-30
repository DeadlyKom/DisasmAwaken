                module ThreeD
                module EdgeCase5A
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #5A
; исходная запись 19, файловые смещения #0274..#028C
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
                JP M, @ThreeD.EdgeCase1A.PointC135                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @ThreeD.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase4A.PointC1F4


                endmodule
                endmodule
