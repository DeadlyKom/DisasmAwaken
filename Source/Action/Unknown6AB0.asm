                module Action
                module Unknown6AB0
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0CED..#0D52
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
                LD A, H
                LD (#9B8A), A
                BIT 7, H
                JR Z, @Action.Unknown6AB0.Point6AC5                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
Point6AC5:      LD (#9B1F), HL
                LD HL, (#D7C4)
                LD A, H
                LD (#9B8B), A
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                BIT 7, H
                JR Z, @Action.Unknown6AB0.Point6AE2                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
Point6AE2:      LD (#9B22), HL
                LD HL, (#D7A2)
                LD A, H
                LD (#9B8C), A
                BIT 7, H
                JR Z, @Action.Unknown6AB0.Point6AF9                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SET 7, H
Point6AF9:      LD (#9B25), HL
                LD A, (#9B81)
                CP #02
                LD DE, #0000
                JR NZ, @Action.Unknown6AB0.Point6B08                            ; переход, если флаг Z сброшен


                LD E, #FF
Point6B08:      LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL #CEFA
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                RET


                endmodule
                endmodule
