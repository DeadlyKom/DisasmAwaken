                module Controls
                module UnknownCA8D
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0A8D..#0AB2
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
Entry:          EXX
                LD BC, #0000
                LD H, B
                LD L, C
                LD D, H
                LD E, L
                DEC HL
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                LD H, B
                LD L, C
                ADD HL, HL
                ADD HL, DE
                ADD HL, BC
                LD D, H
                LD E, L
                LD L, H
                LD H, #00
                LD B, H
                LD C, E
                OR A
                SBC HL, BC
                EX DE, HL
                OR A
                SBC HL, DE
                DEC HL
                LD (#CA8F), HL
                LD A, L
                EXX
                RET


                endmodule
                endmodule
