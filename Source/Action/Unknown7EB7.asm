                module Action
                module Unknown7EB7
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #20F4..#214A
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
Entry:          LD L, (IY + #00)
                LD H, (IY + #01)
                LD E, (IY + #02)
                LD D, (IY + #03)
                LD (#7F0F), DE
                LD (#7F12), HL
                LD L, (IY + #04)
                LD H, (IY + #05)
                LD E, (IY + #06)
                LD D, (IY + #07)
                LD (#7F23), DE
                LD (#7F26), HL
                LD L, (IY + #08)
                LD H, (IY + #09)
                LD E, (IY + #0A)
                LD D, (IY + #0B)
                LD (#7F37), DE
                LD (#7F3A), HL
                CALL @Action.Unknown7F0E.Entry
                PUSH BC
                PUSH DE
                LD E, (IX + #00)
                LD D, (IX + #01)
                LD C, (IX + #02)
                LD B, (IX + #03)
                EXX
                POP HL
                POP DE
                LD C, (IX + #04)
                LD B, (IX + #05)
                EXX
                JP @Action.Unknown6265.Entry


                endmodule
                endmodule
