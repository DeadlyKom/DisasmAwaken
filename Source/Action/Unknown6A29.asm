                module Action
                module Unknown6A29
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0C66..#0CAA
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
Entry:          LD H, (IY + #03)
                LD L, (IY + #02)
                BIT 7, H
                JR Z, @Action.Unknown6A29.Point6A39                             ; переход, если флаг Z установлен


                LD A, H
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
Point6A39:      LD A, H
                OR A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, L
                CP #3C
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD H, (IY + #07)
                LD L, (IY + #06)
                BIT 7, H
                JR Z, @Action.Unknown6A29.Point6A50                             ; переход, если флаг Z установлен


                LD A, H
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
Point6A50:      LD A, H
                OR A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, L
                CP #3C
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD H, (IY + #0B)
                LD L, (IY + #0A)
                BIT 7, H
                JR Z, @Action.Unknown6A29.Point6A67                             ; переход, если флаг Z установлен


                LD A, H
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
Point6A67:      LD A, H
                OR A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, L
                CP #3C
                RET


                endmodule
                endmodule
