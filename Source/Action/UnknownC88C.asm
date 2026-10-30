                module Action
                module UnknownC88C
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #688C..#6EE2
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
                JP P, @Action.UnknownC88C.PointC89E                             ; переход, если флаг Sign сброшен


                EX DE, HL
                LD B, H
                LD C, L
                LD HL, #0000
                OR A
                SBC HL, BC
                EX DE, HL
                INC IXL
PointC89E:      BIT 7, H
                JR Z, @Action.UnknownC88C.PointC8B0                             ; переход, если флаг Z установлен


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
                JR NC, @Action.UnknownC88C.PointC8B8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8B8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8C0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8C0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8C8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8C8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8D0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8D0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8D8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8D8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8E0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8E0:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8E8                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8E8:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8F0                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8F0:      RLA
                EX AF, AF'
                RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC8FA                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC8FA:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC902                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC902:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC90A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC90A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC912                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC912:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC91A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC91A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC922                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC922:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC92A                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC92A:      RLA
                ADC HL, HL
                SBC HL, DE
                JR NC, @Action.UnknownC88C.PointC932                            ; переход, если флаг Carry сброшен


                ADD HL, DE
PointC932:      RLA
                DEC IXL
                JR NZ, @Action.UnknownC88C.PointC93B                            ; переход, если флаг Z сброшен


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
                JR NZ, @Action.UnknownC88C.PointC974                            ; переход, если флаг Z сброшен


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
                JR Z, @Action.UnknownC88C.PointC9CF                             ; переход, если флаг Z установлен


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
                JP PO, @Action.UnknownC88C.PointCA55                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCA55                            ; переход, если флаг P/V сброшен


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
                JP PO, @Action.UnknownC88C.PointCA9E                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCA9E                            ; переход, если флаг P/V сброшен


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

; прежняя физическая граница #CAB3, вход CALL этого банка не установлен
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #6AB3..#6AE2
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
PointCAB3:      SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B
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
                JP PO, @Action.UnknownC88C.PointCAD6                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCAD6                            ; переход, если флаг P/V сброшен


                DEC A
PointCAD6:      LD (#CB3C), A
                LD A, IYH
                SRA A
                LD L, B
                SRA L
                SUB L
                LD L, A
                ADD A, B

; прежняя физическая граница #CAE3, вход CALL этого банка не установлен
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #6AE3..#6EE2
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
PointCAE3:      LD E, (HL)
                LD L, A
                LD A, (HL)
                SUB E
                LD (#CD26), A
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
                LD IXH, A
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
                JP PO, @Action.UnknownC88C.PointCB1F                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCB1F                            ; переход, если флаг P/V сброшен


                DEC A
PointCB1F:      LD (#CC29), A
                RET


                LD H, #98
                LD IY, #9B8D
                BIT 0, (IY + #00)
                JR Z, @Action.UnknownC88C.PointCB37                             ; переход, если флаг Z установлен


                LD A, (#9B13)
                AND #3F
                JP Z, @Action.UnknownC88C.PointCE19                             ; переход, если флаг Z установлен


PointCB37:      LD B, #00
                LD C, #00
                LD D, #00
                LD A, #00
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCB6E                            ; переход, если флаг Z сброшен


                LD A, #00
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCB6C                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCB6C                            ; переход, если флаг P/V сброшен


                DEC A
PointCB6C:      LD IXH, A
PointCB6E:      LD A, #00
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
                JP PO, @Action.UnknownC88C.PointCB87                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCB87                            ; переход, если флаг P/V сброшен


                DEC A
PointCB87:      LD (#D5FC), A
                LD A, #00
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCBBB                            ; переход, если флаг Z сброшен


                LD A, #00
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCBB9                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCBB9                            ; переход, если флаг P/V сброшен


                DEC A
PointCBB9:      LD IXH, A
PointCBBB:      LD A, #00
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
                JP PO, @Action.UnknownC88C.PointCBD4                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCBD4                            ; переход, если флаг P/V сброшен


                DEC A
PointCBD4:      LD (#D62F), A
                LD A, #00
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCC08                            ; переход, если флаг Z сброшен


                LD A, #00
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCC06                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCC06                            ; переход, если флаг P/V сброшен


                DEC A
PointCC06:      LD IXH, A
PointCC08:      LD A, #00
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
                JP PO, @Action.UnknownC88C.PointCC21                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCC21                            ; переход, если флаг P/V сброшен


                DEC A
PointCC21:      LD (#D662), A
                LD B, #00
                LD C, #00
                LD D, #00
                LD A, (#CB3E)
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCC5D                            ; переход, если флаг Z сброшен


                LD A, (#CB54)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCC5B                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCC5B                            ; переход, если флаг P/V сброшен


                DEC A
PointCC5B:      LD IXH, A
PointCC5D:      LD A, (#CB6F)
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
                JP PO, @Action.UnknownC88C.PointCC77                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCC77                            ; переход, если флаг P/V сброшен


                DEC A
PointCC77:      LD (#D61E), A
                LD A, (#CB8B)
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCCAD                            ; переход, если флаг Z сброшен


                LD A, (#CBA1)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCCAB                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCCAB                            ; переход, если флаг P/V сброшен


                DEC A
PointCCAB:      LD IXH, A
PointCCAD:      LD A, (#CBBC)
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
                JP PO, @Action.UnknownC88C.PointCCC7                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCCC7                            ; переход, если флаг P/V сброшен


                DEC A
PointCCC7:      LD (#D651), A
                LD A, (#CBD8)
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
                BIT 0, (IY + #00)
                JR NZ, @Action.UnknownC88C.PointCCFD                            ; переход, если флаг Z сброшен


                LD A, (#CBEE)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCCFB                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCCFB                            ; переход, если флаг P/V сброшен


                DEC A
PointCCFB:      LD IXH, A
PointCCFD:      LD A, (#CC09)
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
                JP PO, @Action.UnknownC88C.PointCD17                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCD17                            ; переход, если флаг P/V сброшен


                DEC A
PointCD17:      LD (#D684), A
                BIT 0, (IY + #00)
                JP NZ, @Action.UnknownC88C.PointCE06                            ; переход, если флаг Z сброшен


                LD B, #00
                LD C, #00
                LD D, #00
                LD A, (#CB3E)
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
                LD A, (#CB54)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCD52                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCD52                            ; переход, если флаг P/V сброшен


                DEC A
PointCD52:      LD IXH, A
                LD A, (#CB6F)
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
                JP PO, @Action.UnknownC88C.PointCD6E                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCD6E                            ; переход, если флаг P/V сброшен


                DEC A
PointCD6E:      LD (#D60D), A
                LD A, (#CB8B)
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
                LD A, (#CBA1)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCD9C                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCD9C                            ; переход, если флаг P/V сброшен


                DEC A
PointCD9C:      LD IXH, A
                LD A, (#CBBC)
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
                JP PO, @Action.UnknownC88C.PointCDB8                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCDB8                            ; переход, если флаг P/V сброшен


                DEC A
PointCDB8:      LD (#D640), A
                LD A, (#CBD8)
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
                LD A, (#CBEE)
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
                ADD A, IXH
                JP PO, @Action.UnknownC88C.PointCDE6                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCDE6                            ; переход, если флаг P/V сброшен


                DEC A
PointCDE6:      LD IXH, A
                LD A, (#CC09)
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
                JP PO, @Action.UnknownC88C.PointCE02                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @Action.UnknownC88C.PointCE02                            ; переход, если флаг P/V сброшен


                DEC A
PointCE02:      LD (#D673), A
                RET


PointCE06:      LD A, (#CB54)
                LD (#D60D), A
                LD A, (#CBA1)
                LD (#D640), A
                LD A, (#CBEE)
                LD (#D673), A
                RET


PointCE19:      LD A, (#CB54)
                LD (#D60D), A
                LD A, (#CBA1)
                LD (#D640), A
                LD A, (#CBEE)
                LD (#D673), A
                LD A, (#9B13)
                AND A
                JR Z, @Action.UnknownC88C.PointCE62                             ; переход, если флаг Z установлен


                JP P, @Action.UnknownC88C.PointCE87                             ; переход, если флаг Sign сброшен


                JP PO, @Action.UnknownC88C.PointCEB2                            ; переход, если флаг P/V сброшен


                LD A, (#CB6F)
                LD (#D5FC), A
                LD A, (#CBBC)
                LD (#D62F), A
                LD A, (#CC09)
                LD (#D662), A
                LD A, (#CB3E)
                NEG
                LD (#D61E), A
                LD A, (#CB8B)
                NEG
                LD (#D651), A
                LD A, (#CBD8)
                NEG
                LD (#D684), A
                RET


PointCE62:      LD A, (#CB3E)
                LD (#D5FC), A
                LD A, (#CB8B)
                LD (#D62F), A
                LD A, (#CBD8)
                LD (#D662), A
                LD A, (#CB6F)
                LD (#D61E), A
                LD A, (#CBBC)
                LD (#D651), A
                LD A, (#CC09)
                LD (#D684), A
                RET


PointCE87:      LD A, (#CB6F)
                NEG
                LD (#D5FC), A
                LD A, (#CBBC)
                NEG
                LD (#D62F), A
                LD A, (#CC09)
                NEG
                LD (#D662), A
                LD A, (#CB3E)
                LD (#D61E), A
                LD A, (#CB8B)
                LD (#D651), A
                LD A, (#CBD8)
                LD (#D684), A
                RET


PointCEB2:      LD A, (#CB3E)
                NEG
                LD (#D5FC), A
                LD A, (#CB8B)
                NEG
                LD (#D62F), A
                LD A, (#CBD8)
                NEG
                LD (#D662), A
                LD A, (#CB6F)
                NEG
                LD (#D61E), A
                LD A, (#CBBC)
                NEG
                LD (#D651), A
                LD A, (#CC09)
                NEG
                LD (#D684), A
                RET

                endmodule
                endmodule
