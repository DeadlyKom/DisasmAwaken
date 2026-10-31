                module Station
                module Unknown7A64
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1D10..#1D2D
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
Entry:          RET C                                                           ; выход, если флаг Carry установлен

                LD A, #14
                CALL @Station.SelectRamBank.Entry
                XOR A
                LD (#E146), A
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD A, #01
                LD (@ShipPanelState.PendingRedraw), A
Point7A78:      XOR A
                LD (@ShipPanelState.OwnedMode), A
                LD HL, (#7A56)
                JP @Station.SwitchItemContour.Entry


                endmodule
                endmodule
