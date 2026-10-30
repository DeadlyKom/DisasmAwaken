                module Action
                module UnknownC6F4
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #66F4..#688B
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
Entry:          LD A, H
                XOR D
                PUSH AF
                BIT 7, D
                JR Z, @Action.UnknownC6F4.PointC702                             ; переход, если флаг Z установлен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
PointC702:      BIT 7, H
                JR Z, @Action.UnknownC6F4.PointC70D                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
PointC70D:      EX DE, HL
                LD A, D
                AND A
                JP Z, @Action.UnknownC6F4.PointC7E0                             ; переход, если флаг Z установлен


                LD A, H
                AND A
                JP Z, @Action.UnknownC6F4.PointC7E5                             ; переход, если флаг Z установлен


                LD BC, #0000
                LD IX, #0000
                ADD HL, HL
                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC73C                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC746                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC750                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC75A                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC764                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP C, @Action.UnknownC6F4.PointC76E                             ; переход, если флаг Carry установлен


                ADD HL, HL
                JP @Action.UnknownC6F4.PointC778


PointC73C:      ADD IX, DE
                ADC HL, BC
                ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC74A                            ; переход, если флаг Carry сброшен


PointC746:      ADD IX, DE
                ADC HL, BC
PointC74A:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC754                            ; переход, если флаг Carry сброшен


PointC750:      ADD IX, DE
                ADC HL, BC
PointC754:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC75E                            ; переход, если флаг Carry сброшен


PointC75A:      ADD IX, DE
                ADC HL, BC
PointC75E:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC768                            ; переход, если флаг Carry сброшен


PointC764:      ADD IX, DE
                ADC HL, BC
PointC768:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC772                            ; переход, если флаг Carry сброшен


PointC76E:      ADD IX, DE
                ADC HL, BC
PointC772:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC77C                            ; переход, если флаг Carry сброшен


PointC778:      ADD IX, DE
                ADC HL, BC
PointC77C:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC786                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC786:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC790                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC790:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC79A                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC79A:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC7A4                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC7A4:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC7AE                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC7AE:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC7B8                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC7B8:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC7C2                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC7C2:      ADD IX, IX
                ADC HL, HL
                JR NC, @Action.UnknownC6F4.PointC7CC                            ; переход, если флаг Carry сброшен


                ADD IX, DE
                ADC HL, BC
PointC7CC:      LD D, IXH
                LD E, IXL
PointC7D0:      POP AF
                RET P                                                           ; выход, если флаг Sign сброшен

                LD B, H
                LD C, L
                LD HL, #0000
                SBC HL, DE
                EX DE, HL
                LD HL, #0000
                SBC HL, BC
                RET


PointC7E0:      LD A, H
                AND A
                JR Z, @Action.UnknownC6F4.PointC836                             ; переход, если флаг Z установлен


                EX DE, HL
PointC7E5:      LD A, L
                LD L, H
                LD C, H
                ADD A, A
                JR C, @Action.UnknownC6F4.PointC803                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC809                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC80F                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC815                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC81B                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC821                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC827                             ; переход, если флаг Carry установлен


                ADD A, A
                JR C, @Action.UnknownC6F4.PointC82D                             ; переход, если флаг Carry установлен


                JP @Action.UnknownC6F4.PointC82F


PointC803:      ADD HL, DE
                ADC A, C
                ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC80B                            ; переход, если флаг Carry сброшен


PointC809:      ADD HL, DE
                ADC A, C
PointC80B:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC811                            ; переход, если флаг Carry сброшен


PointC80F:      ADD HL, DE
                ADC A, C
PointC811:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC817                            ; переход, если флаг Carry сброшен


PointC815:      ADD HL, DE
                ADC A, C
PointC817:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC81D                            ; переход, если флаг Carry сброшен


PointC81B:      ADD HL, DE
                ADC A, C
PointC81D:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC823                            ; переход, если флаг Carry сброшен


PointC821:      ADD HL, DE
                ADC A, C
PointC823:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC829                            ; переход, если флаг Carry сброшен


PointC827:      ADD HL, DE
                ADC A, C
PointC829:      ADD HL, HL
                ADC A, A
                JR NC, @Action.UnknownC6F4.PointC82F                            ; переход, если флаг Carry сброшен


PointC82D:      ADD HL, DE
                ADC A, C
PointC82F:      EX DE, HL
                LD L, A
                LD H, #00
                JP @Action.UnknownC6F4.PointC7D0


PointC836:      RR E
                JR C, @Action.UnknownC6F4.PointC859                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC85F                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC865                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC86B                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC871                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC877                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC87D                             ; переход, если флаг Carry установлен


                RR E
                JR C, @Action.UnknownC6F4.PointC883                             ; переход, если флаг Carry установлен


                JP @Action.UnknownC6F4.PointC887


PointC859:      ADD A, L
                RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC860                            ; переход, если флаг Carry сброшен


PointC85F:      ADD A, L
PointC860:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC866                            ; переход, если флаг Carry сброшен


PointC865:      ADD A, L
PointC866:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC86C                            ; переход, если флаг Carry сброшен


PointC86B:      ADD A, L
PointC86C:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC872                            ; переход, если флаг Carry сброшен


PointC871:      ADD A, L
PointC872:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC878                            ; переход, если флаг Carry сброшен


PointC877:      ADD A, L
PointC878:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC87E                            ; переход, если флаг Carry сброшен


PointC87D:      ADD A, L
PointC87E:      RRA
                RR E
                JR NC, @Action.UnknownC6F4.PointC884                            ; переход, если флаг Carry сброшен


PointC883:      ADD A, L
PointC884:      RRA
                RR E
PointC887:      LD D, A
                LD L, H
                JP @Action.UnknownC6F4.PointC7D0


                endmodule
                endmodule
