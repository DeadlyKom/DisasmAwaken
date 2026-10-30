                module Station
                module Unknown69B8
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #0C64..#0C7A
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
                LD A, #17
                CALL @Station.SelectRamBank.Entry
                CALL #DB00
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD (#6995), DE
                RET


                endmodule
                endmodule
