                module Action
                module Unknown6EAC
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #10E9..#111A
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
Entry:          LD A, #00
                AND A
                RET Z                                                           ; выход, если флаг Z установлен

                LD (#669F), A
                LD HL, (#A78F)
                BIT 7, H
                JR Z, @Action.Unknown6EAC.Point6EC1                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point6EC1:      EX AF, AF'
                LD BC, #0002
                OR A
                SBC HL, BC
                EX AF, AF'
                JR Z, @Action.Unknown6EAC.Point6ED2                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point6ED2:      EX AF, AF'
                JR NC, @Action.Unknown6EAC.Point6ED9                            ; переход, если флаг Carry сброшен


                LD (#A78F), HL
                RET


Point6ED9:      XOR A
                LD (#6EAD), A
                RET


                endmodule
                endmodule
