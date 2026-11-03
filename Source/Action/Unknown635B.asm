                module Action
                module Unknown635B
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0598..#05BC
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
                ; (0) Жёсткий порядок, продолжение в ApplyIndexedDelta.asm
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

                ; JP @Action.ApplyIndexedDelta.Entry, продолжение в ApplyIndexedDelta.asm

                endmodule
                endmodule
