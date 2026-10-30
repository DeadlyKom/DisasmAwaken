                module Action
                module Unknown6C43
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0E80..#0EBA
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
Entry:          RET PE                                                          ; выход, если флаг P/V установлен

                LD HL, (#D9B6)
                BIT 7, H
                JR Z, @Action.Unknown6C43.Point6C54                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
Point6C54:      LD (#9B1F), HL
                LD HL, (#D7C4)
                BIT 7, H
                SET 7, H
                JR Z, @Action.Unknown6C43.Point6C67                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point6C67:      LD (#9B22), HL
                LD HL, (#D7A2)
                BIT 7, H
                JR Z, @Action.Unknown6C43.Point6C7A                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
Point6C7A:      LD (#9B25), HL
                RET


                endmodule
                endmodule
