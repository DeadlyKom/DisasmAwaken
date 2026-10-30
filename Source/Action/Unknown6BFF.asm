                module Action
                module Unknown6BFF
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0E3C..#0E55
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
Entry:          PUSH IY
                POP HL
                LD DE, #9B1E
                LDI
                LDI
                LDI
                INC HL
                LDI
                LDI
                LDI
                INC HL
                LDI
                LDI
                LDI
                ; JP @Action.Unknown6C19.Entry, продолжение в Unknown6C19.asm

                endmodule
                endmodule
