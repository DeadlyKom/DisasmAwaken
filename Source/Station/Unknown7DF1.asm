                module Station
                module Unknown7DF1
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #209D..#20C4
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
Entry:          XOR A
                CALL @Station.Unknown7E1F.Entry
                LD HL, #7A15
                CALL #CBA9
                LD HL, #7A82
                CALL #CBA9
                LD HL, #7A55
                CALL #CBA9
                LD HL, #67E0
                CALL #CBA9
                LD HL, #6945
                CALL #CBA9
                LD HL, #6877
                JP #CBA9


                endmodule
                endmodule
