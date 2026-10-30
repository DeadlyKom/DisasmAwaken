                module Controls
                module UnknownD940
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1940..#195A
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
Entry:          LD A, IXL
                XOR IXH
                LD IXL, A
                LD A, E
                ADD A, #20
                LD E, A
                LD A, L
                ADD A, #20
                LD L, A
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC H
                LD A, #8C
                CP H
                RET NZ                                                          ; выход, если флаг Z сброшен

                POP AF
                LD SP, (#D186)
                POP AF
                RET


                endmodule
                endmodule
