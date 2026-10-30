                module Action
                module UnknownEC08
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #8C08..#8C53
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
Entry:          LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                LD A, (HL)
                PUSH HL
                LD E, A
                LD H, B
                LD L, C
                DEC HL
                ADD HL, HL
                ADC A, #00
                ADD HL, HL
                ADC A, #00
                ADD HL, HL
                ADC A, #00
                ADD HL, HL
                ADC A, #00
                ADD HL, HL
                ADC A, #00
                ADD HL, HL
                ADC A, #00
                EX DE, HL
                LD H, B
                LD L, C
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, DE
                ADC A, #00
                ADD HL, BC
                ADC A, #00
                ADD HL, BC
                ADC A, #00
                ADD HL, BC
                ADC A, #00
                LD D, H
                LD E, L
                LD L, H
                LD H, A
                LD B, #00
                LD C, E
                OR A
                SBC HL, BC
                SBC A, #00
                EX DE, HL
                OR A
                SBC HL, DE
                SBC A, #00
                DEC HL
                EX DE, HL
                POP HL
                LD (HL), A
                DEC HL
                LD (HL), D
                DEC HL
                LD (HL), E
                PUSH DE
                EXX
                POP HL
                RET


                endmodule
                endmodule
