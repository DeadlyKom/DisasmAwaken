                module Controls
                module UnknownF094
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #15B6..#160E
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
Entry:          LD BC, (#9B19)
                LD H, B
                LD A, C
                SRL H
                RRA
                SRL H
                RRA
                SCF
                RR H
                RRA
                LD L, A
                EX DE, HL
                LD A, C
                AND #07
                RLA
                RLA
                LD L, A
                LD H, #00
                LD BC, #F0ED
                ADD HL, BC
                EX DE, HL
                LD BC, #0020
                INC L
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                ADD HL, BC
                DEC L
                INC DE
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC L
                INC DE
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                INC L
                INC DE
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                DEC DE
                DEC DE
                DEC DE
                DEC L
                ADD HL, BC
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                ADD HL, BC
                LD A, (DE)
                XOR (HL)
                LD (HL), A
                RET


                endmodule
                endmodule
