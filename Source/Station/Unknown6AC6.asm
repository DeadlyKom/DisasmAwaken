                module Station
                module Unknown6AC6
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #0D72..#0D89
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
Entry:          LD A, #01
                LD (@TextWindow.Style), A
                LD A, #00
                LD HL, #D1BA
                CALL @Station.SkipLfRecords.Entry
                LD (#6AE0), HL
                CALL @Station.CountTextRows.Entry
                LD (#6A9C), DE
                RET


                endmodule
                endmodule
