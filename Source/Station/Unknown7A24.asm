                module Station
                module Unknown7A24
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1CD0..#1D00
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
                LD A, (@ShipPanelState.Selector)
                OR A
                LD A, (#9849)
                JR Z, @Station.Unknown7A24.Point7A44                            ; переход, если флаг Z установлен


                LD A, (#984A)
Point7A44:      INC A
                EX DE, HL
                LD DE, (#7A83)
                JR Z, @Station.Unknown7A64.Point7A78                            ; переход, если флаг Z установлен


                LD A, #01
                LD (@ShipPanelState.OwnedMode), A
                EX DE, HL
                JP @Station.SwitchItemContour.Entry


                endmodule
                endmodule
