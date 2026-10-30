                module Action
                module Unknown635B
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0598..#05F2
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
                LD A, L
                OR H
                RET Z                                                           ; выход, если флаг Z установлен

                LD BC, #000C
                ADD HL, BC
                SET 0, (HL)
                DEC HL
                LD C, (HL)
                LD (HL), #1A
                LD A, L
                ADD A, #07
                LD L, A
                LD B, (HL)
                LD HL, #0000
                LD (#635C), HL
                LD HL, #EF3B
                LD (#ECA9), HL
                LD A, C
                CP #1A
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, B
                CP #10
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD L, B
                LD H, #00
                LD BC, #634B
                ADD HL, BC
                LD C, (HL)
                LD A, (#9B83)
                AND A
                JR Z, @Action.Unknown635B.Point639A                             ; переход, если флаг Z установлен


                LD A, C
                AND A
                JP M, @Action.Unknown635B.Point639A                             ; переход, если флаг Sign установлен


                ADD A, #0A
                LD C, A
Point639A:      LD A, (#9BCD)
                LD B, A
                ADD A, C
                JP PO, @Action.Unknown635B.Point63A5                            ; переход, если флаг P/V сброшен


                SUB C
                LD A, #7F
Point63A5:      JP P, @Action.Unknown635B.Point63A9                             ; переход, если флаг Sign сброшен


                XOR A
Point63A9:      LD C, A
                LD A, B
                CP #20
                JR NC, @Action.Unknown635B.Point63B1                            ; переход, если флаг Carry сброшен


                SET 5, C
Point63B1:      LD A, C
                LD (#9BCD), A
                RET


                endmodule
                endmodule
