                module Controls
                module UnknownDD5D
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #027F..#02A8
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
Entry:          PUSH BC
                LD HL, (#9B15)
                LD DE, (#9B17)
                LD C, H
                LD B, L
                INC HL
                INC H
                ADD HL, DE
                LD A, E
                ADC A, L
                LD C, A
                ADD HL, BC
                LD A, L
                XOR C
                XOR #75
                LD L, E
                LD E, A
                LD A, H
                XOR B
                XOR #A7
                LD H, D
                LD D, A
                LD (#9B15), HL
                LD (#9B17), DE
                LD A, D
                XOR E
                XOR H
                XOR L
                POP BC
                RET


                endmodule
                endmodule
