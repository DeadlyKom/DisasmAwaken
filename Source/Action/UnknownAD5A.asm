                module Action
                module UnknownAD5A
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4D5A..#4DB6
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
Entry:          PUSH IX
                SRA H
                RR L
                SRA D
                RR E
                OR A
                SBC HL, DE
                PUSH HL
                PUSH BC
                LD D, H
                LD E, L
                CALL #C6F4
                EX DE, HL
                POP BC
                EXX
                PUSH HL
                EXX
                POP HL
                SRA H
                RR L
                SRA B
                RR C
                OR A
                SBC HL, BC
                PUSH HL
                PUSH DE
                LD D, H
                LD E, L
                CALL #C6F4
                POP DE
                ADD HL, DE
                EX DE, HL
                CALL @Action.UnknownAD48.Entry
                LD H, A
                LD L, #00
                PUSH HL
                EXX
                EX DE, HL
                SRA H
                RR L
                SRA B
                RR C
                OR A
                SBC HL, BC
                PUSH HL
                EXX
                POP DE
                POP HL
                CALL @Action.UnknownAE24.Entry
                OR A
                JP P, @Action.UnknownAD5A.PointADAA                             ; переход, если флаг Sign сброшен


                NEG
PointADAA:      POP HL
                POP DE
                ADD A, #80
                PUSH AF
                CALL @Action.UnknownAE24.Entry
                POP BC
                LD C, A
                POP IX
                RET


                endmodule
                endmodule
