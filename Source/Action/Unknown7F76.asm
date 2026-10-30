                module Action
                module Unknown7F76
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #21B3..#21CB
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
Entry:          BIT 7, D
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, D
                CPL
                LD D, A
                LD A, E
                CPL
                LD E, A
                LD A, H
                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                LD BC, #0001
                ADD HL, BC
                DEC BC
                EX DE, HL
                ADC HL, BC
                EX DE, HL
                RET


                endmodule
                endmodule
