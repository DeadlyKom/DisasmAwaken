                module ThreeD
                module EdgeCase52
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; обработчик ребра для индексов таблицы #52
; исходная запись 19, файловые смещения #022F..#024D
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
                JP M, @ThreeD.EdgeCase52.PointC248                              ; переход, если флаг Sign установлен


                LD HL, #CF07
                BIT 0, (HL)
                SET 0, (HL)
                CALL NZ, @ThreeD.UnknownC662.Entry                              ; вызов, если флаг Z сброшен
                JP @ThreeD.EdgeCase42.PointC1C0


PointC248:      CALL @ThreeD.UnknownC5E7.Entry
                JP @ThreeD.EdgeCase02.Entry


                endmodule
                endmodule
