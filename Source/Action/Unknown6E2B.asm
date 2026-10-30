                module Action
                module Unknown6E2B
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #1068..#10A8
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
Entry:          LD A, H
                CP #4A
                JR C, @Action.Unknown6E2B.Point6E3E                             ; переход, если флаг Carry установлен


                CP #4E
                JR NC, @Action.Unknown6E2B.Point6E3E                            ; переход, если флаг Carry сброшен


                LD A, L
                CP #36
                JR C, @Action.Unknown6E2B.Point6E3E                             ; переход, если флаг Carry установлен


                CP #3A
                LD A, #00
                RET C                                                           ; выход, если флаг Carry установлен

Point6E3E:      LD A, H
                CP #47
                JR C, @Action.Unknown6E2B.Point6E51                             ; переход, если флаг Carry установлен


                CP #4A
                JR NC, @Action.Unknown6E2B.Point6E51                            ; переход, если флаг Carry сброшен


                LD A, L
                CP #34
                JR C, @Action.Unknown6E2B.Point6E51                             ; переход, если флаг Carry установлен


                CP #38
                LD A, #01
                RET C                                                           ; выход, если флаг Carry установлен

Point6E51:      LD A, H
                CP #47
                LD A, #03
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, H
                CP #4A
                LD A, #03
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD A, L
                CP #38
                LD A, #03
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, L
                CP #3B
                LD A, #02
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, #03
                RET


                endmodule
                endmodule
