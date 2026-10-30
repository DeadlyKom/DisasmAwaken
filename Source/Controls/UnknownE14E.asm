                module Controls
                module UnknownE14E
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #0670..#06D2
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
Entry:          LD A, B
                AND A
                RRA
                SCF
                RRA
                AND A
                RRA
                XOR B
                AND #F8
                XOR B
                LD H, A
                LD A, C
                RLCA
                RLCA
                RLCA
                XOR B
                AND #C7
                XOR B
                RLCA
                RLCA
                LD L, A
                LD A, C
                AND #07
                ADD A, A
                LD C, A
                ADD A, A
                ADD A, C
                ADD A, E
                LD E, A
                LD A, D
                ADC A, #00
                LD D, A
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                DEC L
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE14E.PointE18D                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE14E.PointE18D                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE18D:      LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                DEC L
                INC H
                LD A, H
                AND #07
                JP NZ, @Controls.UnknownE14E.PointE1A8                          ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Controls.UnknownE14E.PointE1A8                           ; переход, если флаг Carry установлен


                LD A, H
                SUB #08
                LD H, A
PointE1A8:      LD A, (DE)
                OR (HL)
                LD (HL), A
                INC DE
                INC L
                LD A, (DE)
                OR (HL)
                LD (HL), A
                RET


                endmodule
                endmodule
