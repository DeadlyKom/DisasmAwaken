                module Controls
                module UnknownDE10
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #0332..#03BB
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
Entry:          LD HL, (#9BC1)
                LD DE, (#9BC3)
                LD A, (#9BC5)
                CALL @Controls.UnknownDE9A.Entry
                LD (#688B), A
                OR A
                JR NZ, @Controls.UnknownDE10.PointDE25                          ; переход, если флаг Z сброшен


                LD H, #03
PointDE25:      LD A, H
                RLCA
                RLCA
                RLCA
                RLCA
                LD E, A
                LD D, #00
                LD C, L
                DEC C
                PUSH DE
                LD HL, #DF25
                ADD HL, DE
                EX DE, HL
                PUSH BC
                LD HL, #DF65
                LD IX, #9BA4
                LD A, #0F
PointDE3F:      EX AF, AF'
                LD A, (HL)
                AND A
                JP P, @Controls.UnknownDE10.PointDE51                           ; переход, если флаг Sign сброшен


                NEG
                DEC A
                JR Z, @Controls.UnknownDE10.PointDE59                           ; переход, если флаг Z установлен


                LD B, A
                XOR A
PointDE4C:      SUB C
                DJNZ @Controls.UnknownDE10.PointDE4C

                JR @Controls.UnknownDE10.PointDE59


PointDE51:      DEC A
                JR Z, @Controls.UnknownDE10.PointDE59                           ; переход, если флаг Z установлен


                LD B, A
                XOR A
PointDE56:      ADD A, C
                DJNZ @Controls.UnknownDE10.PointDE56

PointDE59:      INC HL
                LD B, (HL)
PointDE5B:      RR B
                JR C, @Controls.UnknownDE10.PointDE63                           ; переход, если флаг Carry установлен


                SRA A
                JR @Controls.UnknownDE10.PointDE5B


PointDE63:      DEC HL
                DEC HL
                ADD A, (HL)
                EX DE, HL
                ADD A, (HL)
                EX DE, HL
                LD (IX + #00), A
                INC DE
                INC IX
                INC HL
                INC HL
                INC HL
                INC HL
                EX AF, AF'
                DEC A
                JP NZ, @Controls.UnknownDE10.PointDE3F                          ; переход, если флаг Z сброшен


                EXX
                POP BC
                EXX
                POP DE
                LD HL, #DEDC
                ADD HL, DE
                EX DE, HL
                LD HL, #7B97
                LD BC, #0006
                LD A, (DE)
                LD (HL), A
                ADD HL, BC
                INC DE
                EXX
                LD B, #08
PointDE8E:      EXX
                LD A, (DE)
                EXX
                ADD A, C
                EXX
                LD (HL), A
                ADD HL, BC
                INC DE
                EXX
                DJNZ @Controls.UnknownDE10.PointDE8E

                RET


                endmodule
                endmodule
