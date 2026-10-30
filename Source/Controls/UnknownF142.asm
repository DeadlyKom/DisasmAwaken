                module Controls
                module UnknownF142
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #1664..#16A9
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
Entry:          LD A, L
                LD C, #2F
                CALL @Controls.UnknownF188.Entry
                LD A, L
                RRCA
                RRCA
                RRCA
                RRCA
                LD C, #2E
                CALL @Controls.UnknownF188.Entry
                BIT 0, B
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, H
                LD C, #2C
                CALL @Controls.UnknownF188.Entry
                LD A, H
                RRCA
                RRCA
                RRCA
                RRCA
                LD C, #2B
                CALL @Controls.UnknownF188.Entry
                BIT 1, B
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, E
                LD C, #29
                CALL @Controls.UnknownF188.Entry
                LD A, E
                RRCA
                RRCA
                RRCA
                RRCA
                LD C, #28
                CALL @Controls.UnknownF188.Entry
                BIT 2, B
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, D
                LD C, #27
                CALL @Controls.UnknownF188.Entry
                LD A, D
                RRCA
                RRCA
                RRCA
                RRCA
                LD C, #26
                ; JP @Controls.UnknownF188.Entry, продолжение в UnknownF188.asm

                endmodule
                endmodule
