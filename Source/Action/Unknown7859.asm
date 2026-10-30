                module Action
                module Unknown7859
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #1A96..#1D02
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
Entry:          LD A, (#9B83)
                AND A
                JP NZ, @Action.Unknown7859.Point799B                            ; переход, если флаг Z сброшен


                LD BC, (#9B7E)
                LD DE, (#9B7B)
                LD HL, (#9B78)
                LD A, #01
                LD (#9B83), A
                LD (#9B82), A
                EXX
                LD A, #10
                LD (#792E), A
                LD HL, (#9BC1)
                LD DE, (#9BC3)
                LD A, (#9BC5)
                EX AF, AF'
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                EX AF, AF'
                CALL #DE9A
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                DEC L
                LD H, #00
                ADD HL, HL
                LD DE, #7799
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD IXL, A
                LD A, (HL)
                LD IXH, A
Point78A1:      CALL @Action.UnknownE9A1.Entry
                RET Z                                                           ; выход, если флаг Z установлен

                EXX
                PUSH HL
                PUSH DE
                PUSH BC
                PUSH BC
                LD C, (IX + #00)
                LD B, (IX + #01)
                XOR A
                INC A
                ADC HL, BC
                JP PO, @Action.Unknown7859.Point78B8                            ; переход, если флаг P/V сброшен


                XOR A
Point78B8:      LD (IY + #00), L
                LD (IY + #01), H
                EX DE, HL
                LD C, (IX + #02)
                LD B, (IX + #03)
                OR A
                ADC HL, BC
                JP PO, @Action.Unknown7859.Point78CC                            ; переход, если флаг P/V сброшен


                XOR A
Point78CC:      LD (IY + #02), L
                LD (IY + #03), H
                POP HL
                LD C, (IX + #04)
                LD B, (IX + #05)
                OR A
                ADC HL, BC
                JP PO, @Action.Unknown7859.Point78E0                            ; переход, если флаг P/V сброшен


                XOR A
Point78E0:      OR A
                JR Z, @Action.Unknown7859.Point7946                             ; переход, если флаг Z установлен


                LD (IY + #04), L
                LD (IY + #05), H
                LD A, (IX + #06)
                LD (IY + #06), A
                LD A, (IX + #07)
                LD (IY + #08), A
                XOR A
                LD (IY + #07), A
                LD (IY + #09), A
                LD (IY + #0A), #09
                LD (IY + #0B), A
                LD (IY + #0C), A
                LD (IY + #0D), A
                LD (IY + #0F), A
                LD (IY + #10), A
                LD (IY + #11), A
                LD (IY + #10), A
                LD (IY + #12), #12
                LD (IY + #13), #FF
                LD (IY + #14), #FF
                LD (IY + #15), #FF
                LD (IY + #16), A
                LD (IY + #17), A
                LD (IY + #18), #10
                LD (#792E), A
                LD (IY + #24), A
                LD BC, #0008
                ADD IX, BC
                LD A, (IX + #01)
                CP #80
Point793F:      POP BC
                POP DE
                POP HL
                RET Z                                                           ; выход, если флаг Z установлен

                JP @Action.Unknown7859.Point78A1


Point7946:      CALL #F03D
                JR @Action.Unknown7859.Point793F


Point794B:      LD (#799C), HL
                LD HL, (#9B79)
                LD A, H
                OR A
                JP P, @Action.Unknown7859.Point795D                             ; переход, если флаг Sign сброшен


                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
Point795D:      LD B, L
                LD C, A
                LD HL, (#9B7C)
                LD A, H
                OR A
                JP P, @Action.Unknown7859.Point796E                             ; переход, если флаг Sign сброшен


                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
Point796E:      LD E, L
                OR C
                LD C, A
                LD HL, (#9B7F)
                LD A, H
                OR A
                JP P, @Action.Unknown7859.Point7980                             ; переход, если флаг Sign сброшен


                CPL
                LD H, A
                LD A, L
                CPL
                LD L, A
                INC HL
                LD A, H
Point7980:      OR C
                JR NZ, @Action.Unknown7859.Point7995                            ; переход, если флаг Z сброшен


                LD A, L
                CP #70
                JR NC, @Action.Unknown7859.Point7995                            ; переход, если флаг Carry сброшен


                LD A, E
                CP #70
                JR NC, @Action.Unknown7859.Point7995                            ; переход, если флаг Carry сброшен


                LD A, B
                CP #70
                JR NC, @Action.Unknown7859.Point7995                            ; переход, если флаг Carry сброшен


                JP @Action.Unknown7859.Entry


Point7995:      CALL @Action.UnknownEB87.Entry
                LD A, H
                XOR L
                RET NZ                                                          ; выход, если флаг Z сброшен

Point799B:      LD DE, #0000
                LD A, D
                CP #23
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, E
                CP #F2
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, #FF
Point79A8:      LD (#7B61), A
                AND A
                JP P, @Action.Unknown7859.Point79CC                             ; переход, если флаг Sign сброшен


                LD A, E
                AND #03
                ADD A, #05
                LD (#7B61), A
                LD A, R
                RRA
                LD A, #20
                JR C, @Action.Unknown7859.Point79C0                             ; переход, если флаг Carry установлен


                LD A, #00
Point79C0:      LD (#79DE), A
                LD A, #06
                JR C, @Action.Unknown7859.Point79C9                             ; переход, если флаг Carry установлен


                LD A, #00
Point79C9:      LD (#7A6A), A
Point79CC:      CALL @Action.UnknownE9A1.Entry
                RET Z                                                           ; выход, если флаг Z установлен

                PUSH IY
                POP IX
                CALL #EB9C
                LD A, L
                XOR H
                AND #1C
                OR #40
                ADD A, #00
                LD (IX + #06), A
                LD L, A
                LD (IX + #0F), #64
                LD A, L
                CALL @Action.UnknownAACC.Entry
                LD A, H
                PUSH AF
                CALL #EB80
                SRA H
                RR L
                LD (IX + #04), L
                LD (IX + #05), H
                PUSH HL
                CALL #EB80
                SRA H
                RR L
                LD (IX + #02), L
                LD (IX + #03), H
                PUSH HL
                CALL #EB80
                SRA H
                RR L
                LD (IX + #00), L
                LD (IX + #01), H
                POP DE
                POP BC
                POP AF
                EX AF, AF'
                LD A, #1A
                EXX
                LD HL, #EC00
                CALL @Action.Unknown6CEF.Entry
                LD A, #01
                LD (#6D39), A
                LD A, (#6D3D)
                CP #1A
                JR NC, @Action.Unknown7859.Point7A34                            ; переход, если флаг Carry сброшен


                LD A, #1A
                LD (#6D3D), A
Point7A34:      LD (IX + #07), #00
                CALL #EBAA
                LD A, L
                AND #03
                BIT 7, L
                JR Z, @Action.Unknown7859.Point7A44                             ; переход, если флаг Z установлен


                NEG
Point7A44:      ADD A, H
                LD (IX + #08), A
                CALL #EBB1
                LD A, L
                AND #1F
                LD (IX + #09), A
                CALL #EBC6
                LD A, L
                AND #55
                LD L, A
                LD A, H
                AND #2A
                AND L
                LD L, A
                LD A, (#7DE4)
                OR L
                LD (IX + #11), A
                CALL #EBB8
                LD (IX + #12), #00
                LD (IX + #0C), #00
                LD (IX + #14), #00
                LD (IX + #15), #FF
                LD (IX + #0B), #FF
                LD HL, (#EBDB)
                LD (IX + #0D), L
                LD (IX + #0E), H
                CALL #EBCD
                LD A, (#7E07)
                OR L
                LD L, A
                LD A, (#7E09)
                LD H, A
                LD A, L
                CP H
                JR C, @Action.Unknown7859.Point7A96                             ; переход, если флаг Carry установлен


                LD A, H
                DEC A
Point7A96:      LD (IX + #13), A
                LD (IX + #10), #20
                XOR A
                LD (IX + #24), A
                LD (IX + #17), A
                LD (IX + #20), #FF
                LD (IX + #21), #FF
                LD (#EBDD), A
                CALL #EB79
                LD A, (IX + #0A)
                LD (IX + #16), A
                LD A, R
                AND #0F
                INC A
                AND #0F
                LD B, A
                LD (IX + #18), B
                JP @Action.Unknown7B58.Point7E89


                endmodule
                endmodule
