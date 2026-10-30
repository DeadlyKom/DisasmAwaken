                module Music
                module UnknownE1CD
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #06CD..#07AD
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
PointE1CF:      LD (#E19F), A
PointE1D2:      EX AF, AF'
PointE1D3:      LD (#DC09), A
                LD A, #00
                DEC A
                JP M, @Music.UnknownE1CD.PointE1ED                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE1CD.PointE1EA                             ; переход, если флаг Z сброшен


                DEC A
                LD HL, #E0EE
                XOR (HL)
                LD (HL), A
                LD A, #00
                JR NZ, @Music.UnknownE1CD.PointE1EA                             ; переход, если флаг Z сброшен


                LD A, #00
PointE1EA:      LD (#E1D7), A
PointE1ED:      LD A, #FF
                LD H, A
                INC A
                JP Z, @Music.UnknownE2CB.PointE2D1                              ; переход, если флаг Z установлен


                LD SP, #0000
                POP DE
                LD A, #00
                LD L, A
                INC A
                CP D
                JR C, @Music.UnknownE1CD.PointE200                              ; переход, если флаг Carry установлен


                LD A, E
PointE200:      LD (#E1F9), A
                ADD HL, HL
                ADD HL, HL
                ADD HL, SP
                LD SP, HL
                POP DE
                LD A, D
                OR #F0
                LD L, A
                LD A, E
                ADD A, A
                LD A, #00
                JR NC, @Music.UnknownE1CD.PointE220                             ; переход, если флаг Carry сброшен


                JP M, @Music.UnknownE1CD.PointE219                              ; переход, если флаг Sign установлен


                SUB #01
                JR @Music.UnknownE1CD.PointE21B


PointE219:      CP #1F
PointE21B:      ADC A, #00
                LD (#E20F), A
PointE220:      ADD A, L
                JR C, @Music.UnknownE1CD.PointE224                              ; переход, если флаг Carry установлен


                XOR A
PointE224:      CP #10
                JR C, @Music.UnknownE1CD.PointE22A                              ; переход, если флаг Carry установлен


                LD A, #0F
PointE22A:      ADD A, #00
                LD L, A
                LD H, #DC
                LD A, (HL)
                SRL E
                JR C, @Music.UnknownE1CD.PointE236                              ; переход, если флаг Carry установлен


                OR #00
PointE236:      EX AF, AF'
                LD A, D
                RLCA
                JR C, @Music.UnknownE1CD.PointE249                              ; переход, если флаг Carry установлен


                LD A, #00
                ADD A, E
                BIT 5, D
                JR Z, @Music.UnknownE1CD.PointE245                              ; переход, если флаг Z установлен


                LD (#E23C), A
PointE245:      LD IXH, A
                JR @Music.UnknownE1CD.PointE25F


PointE249:      LD A, E
                AND #1F
                CP #10
                JR C, @Music.UnknownE1CD.PointE252                              ; переход, если флаг Carry установлен


                OR #F0
PointE252:      ADD A, #00
                BIT 5, D
                JR Z, @Music.UnknownE1CD.PointE25B                              ; переход, если флаг Z установлен


                LD (#E253), A
PointE25B:      EXX
                ADD A, L
                LD L, A
                EXX
PointE25F:      LD A, D
                RRCA
                RRCA
                AND #24
                OR IXL
                LD IXL, A
                POP BC
                LD HL, #0000
                ADD HL, BC
                BIT 6, D
                JR Z, @Music.UnknownE1CD.PointE274                              ; переход, если флаг Z установлен


                LD (#E26A), HL
PointE274:      EX DE, HL
                LD SP, #0000
                POP BC
                LD A, #00
                LD L, A
                INC A
                CP B
                JR C, @Music.UnknownE1CD.PointE281                              ; переход, если флаг Carry установлен


                LD A, C
PointE281:      LD (#E27A), A
                LD H, #00
                ADD HL, SP
                LD A, (#E2B9)
                ADD A, (HL)
                ADD A, A
                JR NC, @Music.UnknownE1CD.PointE28F                             ; переход, если флаг Carry сброшен


                XOR A
PointE28F:      LD L, A
                LD H, #DD
                LD SP, HL
                POP HL
                ADD HL, DE
                LD BC, #0000
                ADD HL, BC
                LD (#DC04), HL
                LD A, #00
                DEC A
                JP M, @Music.UnknownE2CB.PointE2D0                              ; переход, если флаг Sign установлен


                JR NZ, @Music.UnknownE2CB.PointE2CD                             ; переход, если флаг Z сброшен


                EX DE, HL
                LD HL, #0000
                ADD HL, BC
                LD (#E296), HL
                JR @Music.UnknownE2CB.Entry


                endmodule
                endmodule
