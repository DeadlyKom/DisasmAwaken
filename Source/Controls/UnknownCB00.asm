                module Controls
                module UnknownCB00
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0B00..#0E15
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
Entry:          LD HL, #C500
                LD A, (#9B95)
                AND A
                JP Z, @Controls.UnknownCB00.PointCB9A                           ; переход, если флаг Z установлен


                JP M, @Controls.UnknownCB00.PointCB54                           ; переход, если флаг Sign установлен


                RLA
                RLA
                INC A
                INC A
                LD C, A
PointCB12:      LD A, (HL)
                ADD A, C
                JR C, @Controls.UnknownCB00.PointCB1A                           ; переход, если флаг Carry установлен


                CP #5F
                JR C, @Controls.UnknownCB00.PointCB48                           ; переход, если флаг Carry установлен


PointCB1A:      LD A, R
                AND #7F
PointCB1E:      CP C
                JR C, @Controls.UnknownCB00.PointCB24                           ; переход, если флаг Carry установлен


                SUB C
                JR @Controls.UnknownCB00.PointCB1E


PointCB24:      CP #5E
                JR C, @Controls.UnknownCB00.PointCB2A                           ; переход, если флаг Carry установлен


                LD A, #5E
PointCB2A:      ADD A, #00
                LD (HL), A
                CALL @Controls.UnknownCA8D.Entry
                INC L
                CP #01
                JR NC, @Controls.UnknownCB00.PointCB37                          ; переход, если флаг Carry сброшен


                ADD A, #01
PointCB37:      CP #FE
                JR C, @Controls.UnknownCB00.PointCB3D                           ; переход, если флаг Carry установлен


                SUB #01
PointCB3D:      LD (HL), A
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCB12                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCB9A


PointCB48:      LD (HL), A
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCB12                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCB9A


PointCB54:      NEG
                RLA
                RLA
                LD C, A
PointCB59:      LD A, (HL)
                SUB C
                JR C, @Controls.UnknownCB00.PointCB61                           ; переход, если флаг Carry установлен


                CP #01
                JR NC, @Controls.UnknownCB00.PointCB91                          ; переход, если флаг Carry сброшен


PointCB61:      LD A, R
                AND #7F
PointCB65:      CP C
                JR C, @Controls.UnknownCB00.PointCB6B                           ; переход, если флаг Carry установлен


                SUB C
                JR @Controls.UnknownCB00.PointCB65


PointCB6B:      CP #5E
                JR C, @Controls.UnknownCB00.PointCB71                           ; переход, если флаг Carry установлен


                LD A, #5E
PointCB71:      LD B, A
                LD A, #5F
                SUB B
                LD (HL), A
                CALL @Controls.UnknownCA8D.Entry
                INC L
                CP #01
                JR NC, @Controls.UnknownCB00.PointCB80                          ; переход, если флаг Carry сброшен


                ADD A, #01
PointCB80:      CP #FE
                JR C, @Controls.UnknownCB00.PointCB86                           ; переход, если флаг Carry установлен


                SUB #01
PointCB86:      LD (HL), A
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCB59                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCB9A


PointCB91:      LD (HL), A
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCB59                           ; переход, если флаг Carry установлен


PointCB9A:      LD HL, #C501
                LD A, (#9B96)
                AND A
                JP Z, @Controls.UnknownCB00.PointCC38                           ; переход, если флаг Z установлен


                JP P, @Controls.UnknownCB00.PointCBF0                           ; переход, если флаг Sign сброшен


                NEG
                RLA
                RLA
                LD C, A
PointCBAC:      LD A, (HL)
                ADD A, C
                JR C, @Controls.UnknownCB00.PointCBB4                           ; переход, если флаг Carry установлен


                CP #FE
                JR C, @Controls.UnknownCB00.PointCBE4                           ; переход, если флаг Carry установлен


PointCBB4:      CALL @Controls.UnknownCA8D.Entry
PointCBB7:      CP C
                JR C, @Controls.UnknownCB00.PointCBBD                           ; переход, если флаг Carry установлен


                SUB C
                JR @Controls.UnknownCB00.PointCBB7


PointCBBD:      CP #FD
                JR C, @Controls.UnknownCB00.PointCBC3                           ; переход, если флаг Carry установлен


                LD A, #FD
PointCBC3:      ADD A, #00
                LD (HL), A
                LD A, R
                AND #7F
                DEC L
                CP #01
                JR NC, @Controls.UnknownCB00.PointCBD1                          ; переход, если флаг Carry сброшен


                ADD A, #01
PointCBD1:      CP #5F
                JR C, @Controls.UnknownCB00.PointCBD7                           ; переход, если флаг Carry установлен


                SUB #40
PointCBD7:      LD (HL), A
                INC L
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCBAC                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCC38


PointCBE4:      LD (HL), A
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCBAC                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCC38


PointCBF0:      RLA
                RLA
                INC A
                INC A
                LD C, A
PointCBF5:      LD A, (HL)
                SUB C
                JR C, @Controls.UnknownCB00.PointCBFD                           ; переход, если флаг Carry установлен


                CP #01
                JR NC, @Controls.UnknownCB00.PointCC2F                          ; переход, если флаг Carry сброшен


PointCBFD:      CALL @Controls.UnknownCA8D.Entry
PointCC00:      CP C
                JR C, @Controls.UnknownCB00.PointCC06                           ; переход, если флаг Carry установлен


                SUB C
                JR @Controls.UnknownCB00.PointCC00


PointCC06:      CP #FD
                JR C, @Controls.UnknownCB00.PointCC0C                           ; переход, если флаг Carry установлен


                LD A, #FD
PointCC0C:      SUB #FF
                NEG
                LD (HL), A
                LD A, R
                AND #7F
                DEC L
                CP #01
                JR NC, @Controls.UnknownCB00.PointCC1C                          ; переход, если флаг Carry сброшен


                ADD A, #01
PointCC1C:      CP #5F
                JR C, @Controls.UnknownCB00.PointCC22                           ; переход, если флаг Carry установлен


                SUB #40
PointCC22:      LD (HL), A
                INC L
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCBF5                           ; переход, если флаг Carry установлен


                JP @Controls.UnknownCB00.PointCC38


PointCC2F:      LD (HL), A
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCBF5                           ; переход, если флаг Carry установлен


PointCC38:      LD A, (#9B97)
                NEG
                AND A
                RET Z                                                           ; выход, если флаг Z установлен

                LD L, A
                JP P, @Controls.UnknownCB00.PointCC45                           ; переход, если флаг Sign сброшен


                NEG
PointCC45:      RLA
                RLA
                LD (#CE1E), A
                LD (#CE65), A
                LD H, #99
                LD A, (HL)
                LD (#CCD2), A
                NEG
                LD (#CD9D), A
                LD A, L
                ADD A, #40
                LD L, A
                LD A, (HL)
                LD (#CC7E), A
                LD (#CD49), A
                LD A, L
                SUB #40
                LD HL, #CE16
                JP P, @Controls.UnknownCB00.PointCC6F                           ; переход, если флаг Sign сброшен


                LD HL, #CE5D
PointCC6F:      LD (#CD31), HL
                LD (#CDFC), HL
                LD HL, #C500
PointCC78:      LD A, (HL)
                SUB #30
                EXX
                LD C, A
                LD E, #00
                XOR E
                EX AF, AF'
                LD A, E
                AND A
                JP P, @Controls.UnknownCB00.PointCC89                           ; переход, если флаг Sign сброшен


                NEG
                LD E, A
PointCC89:      LD A, C
                AND A
                JP P, @Controls.UnknownCB00.PointCC91                           ; переход, если флаг Sign сброшен


                NEG
                LD C, A
PointCC91:      XOR A
                RR E
                JR NC, @Controls.UnknownCB00.PointCC97                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCC97:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCC9D                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCC9D:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCA3                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCA3:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCA9                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCA9:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCAF                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCAF:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCB5                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCB5:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCBB                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCBB:      RRA
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UnknownCB00.PointCCC9                           ; переход, если флаг Sign сброшен


                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
PointCCC9:      EX DE, HL
                EXX
                INC L
                LD A, (HL)
                SUB #80
                EXX
                LD C, A
                LD E, #00
                XOR E
                EX AF, AF'
                LD A, E
                AND A
                JP P, @Controls.UnknownCB00.PointCCDD                           ; переход, если флаг Sign сброшен


                NEG
                LD E, A
PointCCDD:      LD A, C
                AND A
                JP P, @Controls.UnknownCB00.PointCCE5                           ; переход, если флаг Sign сброшен


                NEG
                LD C, A
PointCCE5:      XOR A
                RR E
                JR NC, @Controls.UnknownCB00.PointCCEB                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCEB:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCF1                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCF1:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCF7                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCF7:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCCFD                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCCFD:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD03                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD03:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD09                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD09:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD0F                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD0F:      RRA
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UnknownCB00.PointCD1D                           ; переход, если флаг Sign сброшен


                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
PointCD1D:      ADD HL, DE
                LD BC, #0030
                ADD HL, BC
                LD A, H
                AND A
                JR NZ, @Controls.UnknownCB00.PointCD2F                          ; переход, если флаг Z сброшен


                LD A, L
                CP #01
                JR C, @Controls.UnknownCB00.PointCD2F                           ; переход, если флаг Carry установлен


                CP #5F
                JR C, @Controls.UnknownCB00.PointCD3F                           ; переход, если флаг Carry установлен


PointCD2F:      EXX
                CALL @Controls.UnknownCE16.Entry
                LD (HL), D
                DEC L
                LD (HL), E
                INC L
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCC78                           ; переход, если флаг Carry установлен


                RET


PointCD3F:      LD (#CE0B), A
                EXX
                LD A, (HL)
                SUB #80
                EXX
                LD C, A
                LD E, #00
                XOR E
                EX AF, AF'
                LD A, E
                AND A
                JP P, @Controls.UnknownCB00.PointCD54                           ; переход, если флаг Sign сброшен


                NEG
                LD E, A
PointCD54:      LD A, C
                AND A
                JP P, @Controls.UnknownCB00.PointCD5C                           ; переход, если флаг Sign сброшен


                NEG
                LD C, A
PointCD5C:      XOR A
                RR E
                JR NC, @Controls.UnknownCB00.PointCD62                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD62:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD68                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD68:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD6E                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD6E:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD74                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD74:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD7A                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD7A:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD80                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD80:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCD86                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCD86:      RRA
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UnknownCB00.PointCD94                           ; переход, если флаг Sign сброшен


                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
PointCD94:      EX DE, HL
                EXX
                DEC L
                LD A, (HL)
                SUB #30
                EXX
                LD C, A
                LD E, #00
                XOR E
                EX AF, AF'
                LD A, E
                AND A
                JP P, @Controls.UnknownCB00.PointCDA8                           ; переход, если флаг Sign сброшен


                NEG
                LD E, A
PointCDA8:      LD A, C
                AND A
                JP P, @Controls.UnknownCB00.PointCDB0                           ; переход, если флаг Sign сброшен


                NEG
                LD C, A
PointCDB0:      XOR A
                RR E
                JR NC, @Controls.UnknownCB00.PointCDB6                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDB6:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDBC                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDBC:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDC2                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDC2:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDC8                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDC8:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDCE                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDCE:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDD4                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDD4:      RRA
                RR E
                JR NC, @Controls.UnknownCB00.PointCDDA                          ; переход, если флаг Carry сброшен


                ADD A, C
PointCDDA:      RRA
                INC A
                LD E, A
                EX AF, AF'
                LD D, #00
                JP P, @Controls.UnknownCB00.PointCDE8                           ; переход, если флаг Sign сброшен


                DEC D
                LD A, E
                CPL
                LD E, A
                INC DE
PointCDE8:      ADD HL, DE
                LD BC, #0080
                ADD HL, BC
                LD A, H
                AND A
                JR NZ, @Controls.UnknownCB00.PointCDFA                          ; переход, если флаг Z сброшен


                LD A, L
                CP #01
                JR C, @Controls.UnknownCB00.PointCDFA                           ; переход, если флаг Carry установлен


                CP #FE
                JR C, @Controls.UnknownCB00.PointCE09                           ; переход, если флаг Carry установлен


PointCDFA:      EXX
                CALL @Controls.UnknownCE16.Entry
                LD (HL), E
                INC L
                LD (HL), D
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCC78                           ; переход, если флаг Carry установлен


                RET


PointCE09:      EXX
                LD (HL), #00
                INC L
                LD (HL), A
                INC L
                LD A, L
                CP #46
                JP C, @Controls.UnknownCB00.PointCC78                           ; переход, если флаг Carry установлен


                RET


                endmodule
                endmodule
