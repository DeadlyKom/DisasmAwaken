                module Action
                module UnknownE4A6
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #84A6..#84DA
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
Entry:          LD SP, #0000
                LD A, (#9BA1)
                LD H, #8F
                JP @Action.UnknownE4FF.Entry


PointE4B1:      PUSH HL
                LD (#E4D6), SP
                INC L
                INC L
                INC L
                LD SP, HL
                POP HL
                LD (#9B8D), HL
                POP HL
                LD (#9B12), HL
                DEC SP
                POP AF
                LD (#9B14), A
                POP HL
                LD (#D9B6), HL
                POP DE
                LD (#D7C4), DE
                POP BC
                LD (#D7A2), BC
                LD SP, #0000
                CALL @Action.UnknownECA8.Entry
                endmodule
                endmodule
