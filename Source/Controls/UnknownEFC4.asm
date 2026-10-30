                module Controls
                module UnknownEFC4
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #14E6..#1512
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
Entry:          SUB #20
                LD L, A
                RES 0, L
                LD H, #00
                LD D, H
                LD E, L
                ADD HL, HL
                ADD HL, DE
                LD BC, #C600
                ADD HL, BC
                EX DE, HL
                EX AF, AF'
                LD C, #00
                LD A, C
                CP #18
                JR C, @Controls.UnknownEFC4.PointEFE3                           ; переход, если флаг Carry установлен


                PUSH DE
                CALL @Controls.UnknownED28.Entry
                POP DE
                LD C, #00
PointEFE3:      LD B, C
                LD H, #50
                LD A, #F4
                SRL B
                ADD A, B
                LD L, A
                INC C
                LD A, C
                LD (#EFD6), A
                ; JP @Controls.UnknownEFF1.Entry, продолжение в UnknownEFF1.asm

                endmodule
                endmodule
