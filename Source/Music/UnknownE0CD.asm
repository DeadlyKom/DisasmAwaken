                module Music
                module UnknownE0CD
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #05CD..#06AF
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
Entry:          LD A, #00
PointE0CF:      LD (#E09F), A
PointE0D2:      EX AF, AF'
PointE0D3:      LD (#DC08), A
                LD A, #00
                DEC A
                JP M, @Music.UnknownE0CD.PointE0ED                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE0CD.PointE0EA                             ; переход, если флаг Z сброшен


                DEC A
                LD HL, #DFEF
                XOR (HL)
                LD (HL), A
                LD A, #00
                JR NZ, @Music.UnknownE0CD.PointE0EA                             ; переход, если флаг Z сброшен


                LD A, #00
PointE0EA:      LD (#E0D7), A
PointE0ED:      LD A, #FF
                LD H, A
                INC A
                JP Z, @Music.UnknownE1CD.PointE1D3                              ; переход, если флаг Z установлен


                LD SP, #0000
                POP DE
                LD A, #00
                LD L, A
                INC A
                CP D
                JR C, @Music.UnknownE0CD.PointE100                              ; переход, если флаг Carry установлен


                LD A, E
PointE100:      LD (#E0F9), A
                ADD HL, HL
                SLA L
                ADD HL, SP
                LD SP, HL
                POP DE
                LD A, D
                OR #F0
                LD L, A
                LD A, E
                ADD A, A
                LD A, #00
                JR NC, @Music.UnknownE0CD.PointE121                             ; переход, если флаг Carry сброшен


                JP M, @Music.UnknownE0CD.PointE11A                              ; переход, если флаг Sign установлен


                SUB #01
                JR @Music.UnknownE0CD.PointE11C


PointE11A:      CP #1F
PointE11C:      ADC A, #00
                LD (#E110), A
PointE121:      ADD A, L
                JR C, @Music.UnknownE0CD.PointE125                              ; переход, если флаг Carry установлен


                XOR A
PointE125:      CP #10
                JR C, @Music.UnknownE0CD.PointE12B                              ; переход, если флаг Carry установлен


                LD A, #0F
PointE12B:      ADD A, #00
                LD L, A
                LD H, #DC
                LD A, (HL)
                SRL E
                JR C, @Music.UnknownE0CD.PointE137                              ; переход, если флаг Carry установлен


                OR #00
PointE137:      EX AF, AF'
                LD A, D
                RLCA
                JR C, @Music.UnknownE0CD.PointE14A                              ; переход, если флаг Carry установлен


                LD A, #00
                ADD A, E
                BIT 5, D
                JR Z, @Music.UnknownE0CD.PointE146                              ; переход, если флаг Z установлен


                LD (#E13D), A
PointE146:      LD IXH, A
                JR @Music.UnknownE0CD.PointE160


PointE14A:      LD A, E
                AND #1F
                CP #10
                JR C, @Music.UnknownE0CD.PointE153                              ; переход, если флаг Carry установлен


                OR #F0
PointE153:      ADD A, #00
                BIT 5, D
                JR Z, @Music.UnknownE0CD.PointE15C                              ; переход, если флаг Z установлен


                LD (#E154), A
PointE15C:      EXX
                ADD A, L
                LD L, A
                EXX
PointE160:      LD A, D
                RRCA
                RRCA
                RRCA
                AND #12
                OR IXL
                LD IXL, A
                POP BC
                LD HL, #0000
                ADD HL, BC
                BIT 6, D
                JR Z, @Music.UnknownE0CD.PointE176                              ; переход, если флаг Z установлен


                LD (#E16C), HL
PointE176:      EX DE, HL
                LD SP, #0000
                POP BC
                LD A, #00
                LD L, A
                INC A
                CP B
                JR C, @Music.UnknownE0CD.PointE183                              ; переход, если флаг Carry установлен


                LD A, C
PointE183:      LD (#E17C), A
                LD H, #00
                ADD HL, SP
                LD A, (#E1BB)
                ADD A, (HL)
                ADD A, A
                JR NC, @Music.UnknownE0CD.PointE191                             ; переход, если флаг Carry сброшен


                XOR A
PointE191:      LD L, A
                LD H, #DD
                LD SP, HL
                POP HL
                ADD HL, DE
                LD BC, #0000
                ADD HL, BC
                LD (#DC02), HL
                LD A, #00
                DEC A
                JP M, @Music.UnknownE1CD.PointE1D2                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE1CD.PointE1CF                             ; переход, если флаг Z сброшен


                EX DE, HL
                LD HL, #0000
                ADD HL, BC
                LD (#E198), HL
                JR @Music.UnknownE1CD.Entry


                endmodule
                endmodule
