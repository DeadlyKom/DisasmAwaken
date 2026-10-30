                module ThreeD
                module EdgeCase96
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #96
; исходная запись 19, файловые смещения #03D6..#03EE
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
                CALL @ThreeD.UnknownC4D4.Entry
                CALL @ThreeD.UnknownC681.Entry
                JP M, @ThreeD.EdgeCase86.PointC35C                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 2, (HL)
                SET 2, (HL)
                CALL NZ, @ThreeD.UnknownC64C.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase16.PointC104


                endmodule
                endmodule
