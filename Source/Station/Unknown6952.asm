                module Station
                module Unknown6952
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #0BFE..#0C0E
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
Entry:          LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, (@ShipPanelState.Selector)
                CALL #E154
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET


                endmodule
                endmodule
