                module ThreeD
                module UnknownC88C
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 19, файловые смещения #088C..#0AB2
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
Entry:          LD IXL, #00
                JP P, @ThreeD.UnknownC88C.PointC89E                             ; переход, если флаг Sign сброшен


                EX DE, HL
                LD B, H
                LD C, L
                LD HL, #0000
                OR A
                SBC HL, BC
                EX DE, HL
                INC IXL
PointC89E:      BIT 7, H
                JR Z, @ThreeD.UnknownC88C.PointC8B0                             ; переход, если флаг Z установлен


                EX AF, AF'
                CPL
                EX AF, AF'
                CPL
                LD B, H
                LD C, L
                LD HL, #0000
                SCF
                SBC HL, BC
                INC IXL
PointC8B0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8B8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8B8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8C0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8C0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8C8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8C8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8D0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8D0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8D8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8D8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8E0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8E0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8E8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8E8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8F0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8F0:      RLA
                EX AF, AF'
                RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC8FA                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8FA:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC902                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC902:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC90A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC90A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC912                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC912:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC91A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC91A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC922                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC922:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC92A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC92A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @ThreeD.UnknownC88C.PointC932                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC932:      RLA
                DEC IXL
                JR NZ, @ThreeD.UnknownC88C.PointC93B                            ; переход, если флаг Z сброшен


                LD L, A
                EX AF, AF'
                LD H, A
                RET


PointC93B:      CPL
                LD L, A
                EX AF, AF'
                CPL
                LD H, A
                RET


                LD A, #01
                LD (#CF03), A
                LD A, (#CF0F)
                CP #F0
                JR NZ, @ThreeD.UnknownC88C.PointC974                            ; переход, если флаг Z сброшен


                LD B, A
                LD A, (#CF1F)
                LD (#CF0F), A
                LD A, B
                LD (#CF1F), A
                LD HL, (#CF0B)
                LD DE, (#CF1B)
                LD (#CF1B), HL
                LD (#CF0B), DE
                LD HL, (#CF0D)
                LD DE, (#CF1D)
                LD (#CF1D), HL
                LD (#CF0D), DE
PointC974:      XOR A
                LD (#9BA3), A
                LD A, (#CF0F)
                CPL
                AND #F0
                LD L, A
                LD A, (#CF1F)
                AND #0F
                OR L
                LD L, A
                LD H, #CF
                LD E, (HL)
                INC H
                LD D, (HL)
                EX DE, HL
                LD DE, #C993
                PUSH DE
                PUSH DE
                PUSH DE
                JP (HL)


                LD A, (#9BA3)
                POP DE
                POP DE
                CP #04
                RET


                LD HL, #9B8D
                BIT 0, (HL)
                JR Z, @ThreeD.UnknownC88C.PointC9CF                             ; переход, если флаг Z установлен


                LD A, (#9B13)
                LD B, A
                ADD A, #40
                LD H, #99
                LD L, A
                LD A, (HL)
                LD (#CB38), A
                LD (#CC29), A
                LD L, B
                LD A, (HL)
                LD (#CC25), A
                NEG
                LD (#CB3C), A
                XOR A
                LD (#CD22), A
                LD (#CB3A), A
                LD (#CC27), A
                LD (#CD26), A
                LD A, #7F
                LD (#CD24), A
                RET


PointC9CF:      LD A, (#9B12)
                LD H, #99
                LD L, A
                LD B, (HL)
                ADD A, #40
                LD L, A
                LD C, (HL)
                LD A, (#9B13)
                LD L, A
                LD A, (HL)
                LD IXL, A
                LD A, L
                ADD A, #40
                LD L, A
                LD A, (HL)
                LD IYL, A
                LD A, (#9B14)
                LD L, A
                LD A, (HL)
                LD D, A
                NEG
                LD (#CD22), A
                LD A, L
                ADD A, #40
                LD L, A
                LD A, (HL)
                LD IYH, A
                LD H, #98
                LD E, IYL
                SRA A
                LD L, E
                SRA L
                SUB L
                LD L, A
                ADD A, E
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (#CB38), A
                LD A, IXL
                LD E, IYH
                SRA A
                LD L, E
                SRA L
                SUB L
                LD L, A
                ADD A, E
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (#CC25), A
                LD A, IXL
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                LD A, IYL
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                ADD A, IXH
                JP PO, @ThreeD.UnknownC88C.PointCA55                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownC88C.PointCA55                            ; переход, если флаг P/V сброшен


                DEC A
PointCA55:      LD (#CB3A), A
                LD A, IYH
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (#CD24), A
                LD A, IYL
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                LD A, IXL
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                SRA A
                LD L, D
                SRA L
                SUB L
                LD L, A
                ADD A, D
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                SUB IXH
                JP PO, @ThreeD.UnknownC88C.PointCA9E                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownC88C.PointCA9E                            ; переход, если флаг P/V сброшен


                DEC A
PointCA9E:      LD (#CC27), A
                LD A, IXL
                SRA A
                LD L, C
                SRA L
                SUB L
                LD L, A
                ADD A, C
                LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD IXH, A
                LD A, IYL
                ; JP @ThreeD.UnknownCAB3.Entry, продолжение в UnknownCAB3.asm

                endmodule
                endmodule
