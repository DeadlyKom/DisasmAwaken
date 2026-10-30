                module Action
                module UnknownE5A0
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #85A0..#8654
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
Entry:          ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD A, #7D
                SUB H
                LD B, A
                LD A, IXL
                LD L, A
                LD A, IXH
                LD H, A
                LD SP, HL
                LD HL, #0000
                LD DE, #0000
                OR A
                SBC HL, DE
                POP DE
                LD A, D
                CP #80
                JR Z, @Action.UnknownE5A0.PointE604                             ; переход, если флаг Z установлен


                AND A
                ADC HL, DE
                JP PE, @Action.UnknownE658.Entry                                ; переход, если флаг P/V установлен


                LD A, H
                JP P, @Action.UnknownE5A0.PointE5C9                             ; переход, если флаг Sign сброшен


                CPL
PointE5C9:      CP B
                JP NC, @Action.UnknownE658.Entry                                ; переход, если флаг Carry сброшен


                PUSH HL
                LD HL, #0000
                LD DE, #0000
                OR A
                SBC HL, DE
                INC SP
                INC SP
                POP DE
                AND A
                ADC HL, DE
                JP PE, @Action.UnknownE658.Entry                                ; переход, если флаг P/V установлен


                LD A, H
                JP P, @Action.UnknownE5A0.PointE5E5                             ; переход, если флаг Sign сброшен


                CPL
PointE5E5:      CP B
                JR NC, @Action.UnknownE658.Entry                                ; переход, если флаг Carry сброшен


                PUSH HL
                LD HL, #0000
                LD DE, #0000
                OR A
                SBC HL, DE
                INC SP
                INC SP
                POP DE
                AND A
                ADC HL, DE
                JP PE, @Action.UnknownE658.Entry                                ; переход, если флаг P/V установлен


                LD A, H
                JP P, @Action.UnknownE5A0.PointE600                             ; переход, если флаг Sign сброшен


                CPL
PointE600:      CP B
                JR NC, @Action.UnknownE658.Entry                                ; переход, если флаг Carry сброшен


                PUSH HL
PointE604:      LD SP, #0000
                LD A, (#9B82)
                AND A
                JP Z, @Action.UnknownE685.Entry                                 ; переход, если флаг Z установлен


                LD D, #12
                CALL @Action.UnknownE98D.Entry
                JP Z, @Action.UnknownE685.Entry                                 ; переход, если флаг Z установлен


                LD A, (IY + #05)
                OR A
                JP P, @Action.UnknownE5A0.PointE61E                             ; переход, если флаг Sign сброшен


                CPL
PointE61E:      LD B, A
                LD A, (IY + #03)
                OR A
                JP P, @Action.UnknownE5A0.PointE627                             ; переход, если флаг Sign сброшен


                CPL
PointE627:      LD C, A
                LD A, (IY + #01)
                OR A
                JP P, @Action.UnknownE5A0.PointE630                             ; переход, если флаг Sign сброшен


                CPL
PointE630:      CP C
                JR NC, @Action.UnknownE5A0.PointE634                            ; переход, если флаг Carry сброшен


                LD A, C
PointE634:      CP B
                JR NC, @Action.UnknownE5A0.PointE638                            ; переход, если флаг Carry сброшен


                LD A, B
PointE638:      CP #08
                JR C, @Action.UnknownE5A0.PointE643                             ; переход, если флаг Carry установлен


                LD A, #80
                LD (#E644), A
                JR @Action.UnknownE685.Entry


PointE643:      LD A, #00
                AND A
                JP P, @Action.UnknownE685.Entry                                 ; переход, если флаг Sign сброшен


                LD A, #18
                LD (#E644), A
                PUSH DE
                LD DE, #F3B9
                CALL @Action.Unknown6040.Entry
                endmodule
                endmodule
