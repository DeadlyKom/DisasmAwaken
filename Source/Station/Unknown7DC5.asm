                module Station
                module Unknown7DC5
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #2071..#208C
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
                LD (#6ACC), A
                LD HL, #6AB6
                CALL @Station.RestoreItemBounds.Entry
                LD HL, #7B40
                CALL #CBA9
                LD HL, #7B25
                CALL #CBA9
                LD HL, #7227
                JP #CBA9


                endmodule
                endmodule
