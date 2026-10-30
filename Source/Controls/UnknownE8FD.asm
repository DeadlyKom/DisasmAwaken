                module Controls
                module UnknownE8FD
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #0E1F..#0E94
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
Entry:          LD C, A
                AND A
                JR Z, @Controls.UnknownE8FD.PointE928                           ; переход, если флаг Z установлен


                CPL
                AND #07
                LD A, C
                JR NZ, @Controls.UnknownE8FD.PointE90C                          ; переход, если флаг Z сброшен


                ADD A, #08
                AND #F8
                LD C, A
PointE90C:      RRCA
                RRCA
                RRCA
                AND #07
                JR Z, @Controls.UnknownE8FD.PointE928                           ; переход, если флаг Z установлен


                LD B, A
                LD DE, #05AA
PointE917:      LD (HL), E
                INC H
                LD (HL), E
                INC H
                LD (HL), E
                INC H
                LD (HL), E
                INC H
                LD (HL), E
                INC H
                LD (HL), E
                LD A, H
                SUB D
                LD H, A
                INC L
                DJNZ @Controls.UnknownE8FD.PointE917

PointE928:      LD A, C
                EX AF, AF'
                LD A, C
                AND #07
                JR Z, @Controls.UnknownE8FD.PointE949                           ; переход, если флаг Z установлен


                LD C, A
                LD B, #00
                EX DE, HL
                LD HL, #E973
                ADD HL, BC
                LD A, (HL)
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                INC D
                LD (DE), A
                LD A, D
                SUB #05
                LD D, A
                EX DE, HL
                INC L
PointE949:      EX AF, AF'
                LD C, A
                AND #07
                LD A, C
                JR Z, @Controls.UnknownE8FD.PointE952                           ; переход, если флаг Z установлен


                ADD A, #08
PointE952:      RRCA
                RRCA
                RRCA
                AND #07
                SUB #06
                RET NC                                                          ; выход, если флаг Carry сброшен

                NEG
                LD B, A
                LD DE, #0005
                XOR A
PointE961:      LD (HL), D
                INC H
                LD (HL), D
                INC H
                LD (HL), D
                INC H
                LD (HL), D
                INC H
                LD (HL), D
                INC H
                LD (HL), D
                LD A, H
                SUB E
                LD H, A
                INC L
                DJNZ @Controls.UnknownE8FD.PointE961

                RET


                endmodule
                endmodule
