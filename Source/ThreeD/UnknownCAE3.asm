                module ThreeD
                module UnknownCAE3
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 19, файловые смещения #0AE3..#0EE2
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
Entry:          LD E, (HL)
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
                JP PO, @ThreeD.UnknownCAE3.PointCB1F                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCB1F                            ; переход, если флаг P/V сброшен


                DEC A
PointCB1F:      LD (#CC29), A
                RET


                LD H, #98
                LD IY, #9B8D
                BIT 0, (IY + #00)
                JR Z, @ThreeD.UnknownCAE3.PointCB37                             ; переход, если флаг Z установлен


                LD A, (#9B13)
                AND #3F
                JP Z, @ThreeD.UnknownCAE3.PointCE19                             ; переход, если флаг Z установлен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCB6E                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCB6C                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCB6C                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCB87                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCB87                            ; переход, если флаг P/V сброшен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCBBB                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCBB9                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCBB9                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCBD4                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCBD4                            ; переход, если флаг P/V сброшен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCC08                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCC06                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCC06                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCC21                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCC21                            ; переход, если флаг P/V сброшен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCC5D                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCC5B                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCC5B                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCC77                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCC77                            ; переход, если флаг P/V сброшен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCCAD                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCCAB                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCCAB                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCCC7                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCCC7                            ; переход, если флаг P/V сброшен


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
                JR NZ, @ThreeD.UnknownCAE3.PointCCFD                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCCFB                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCCFB                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCD17                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCD17                            ; переход, если флаг P/V сброшен


                DEC A
PointCD17:      LD (#D684), A
                BIT 0, (IY + #00)
                JP NZ, @ThreeD.UnknownCAE3.PointCE06                            ; переход, если флаг Z сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCD52                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCD52                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCD6E                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCD6E                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCD9C                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCD9C                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCDB8                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCDB8                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCDE6                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCDE6                            ; переход, если флаг P/V сброшен


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
                JP PO, @ThreeD.UnknownCAE3.PointCE02                            ; переход, если флаг P/V сброшен


                NEG
                JP PO, @ThreeD.UnknownCAE3.PointCE02                            ; переход, если флаг P/V сброшен


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
                JR Z, @ThreeD.UnknownCAE3.PointCE62                             ; переход, если флаг Z установлен


                JP P, @ThreeD.UnknownCAE3.PointCE87                             ; переход, если флаг Sign сброшен


                JP PO, @ThreeD.UnknownCAE3.PointCEB2                            ; переход, если флаг P/V сброшен


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
