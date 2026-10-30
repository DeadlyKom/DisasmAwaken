                module Station
                module Unknown7044
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #12F0..#131C
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
Entry:          LD (#983A), A
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                CALL #C000
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.DrawItem34.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET


Point7061:      LD DE, #1E23
                LD HL, #7071
                LD A, #FF
                CALL @Station.UpdateRowHover.Entry
                RET Z                                                           ; выход, если флаг Z установлен

                LD (#7068), A
                RET


                endmodule
                endmodule
