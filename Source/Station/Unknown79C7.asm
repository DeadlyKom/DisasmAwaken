                module Station
                module Unknown79C7
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1C73..#1CC0
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
Entry:          LD A, (#67D7)
                INC A
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, (#67D7)
                LD (#E146), A
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD A, #00
                OR A
                LD C, #01
                JR Z, @Station.Unknown79C7.Point79E4                            ; переход, если флаг Z установлен


                INC C
Point79E4:      LD A, (#6906)
                OR A
                LD A, C
                JR Z, @Station.Unknown79C7.Point79ED                            ; переход, если флаг Z установлен


                ADD A, #02
Point79ED:      LD (#983A), A
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                CALL #C000
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.EndScreenUpdate.Entry
                LD DE, (#67E1)
                CALL @Station.DropItemDraw.Entry
                CALL @Station.Unknown6780.Entry
                XOR A
                LD (@ActiveItemState.Active), A
                RET


                endmodule
                endmodule
