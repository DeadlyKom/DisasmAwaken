                module Station
                module DrawItem26
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 26 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0B23..#0B77
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
Entry:          LD HL, #0000
                CALL @Station.SetBandFillMode.Entry
                CALL #C287
                CALL #CCD4
                LD HL, (#6878)
                CALL @Station.CheckItemRect.Entry
                LD HL, #9A58
                JR NC, @Station.DrawItem26.Point6891                            ; переход, если флаг Carry сброшен


                LD HL, @Station.Unknown68EA.Entry
Point6891:      LD (#9A89), HL
                EX DE, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                EXX
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD DE, #0000
                LD A, (#AEB3)
                SUB #0D
                LD L, A
                LD A, (#AEAB)
                SUB #0E
                LD H, A
                LD A, (@ShipPanelState.Selector)
                CALL #E13C
                LD HL, (#9A89)
                LD DE, #9A58
                OR A
                SBC HL, DE
                JR Z, @Station.DrawItem26.Point68C6                             ; переход, если флаг Z установлен


                HALT
                LD A, (@ShipPanelState.Selector)
                CALL #E07F
Point68C6:      LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET


                endmodule
                endmodule
