                module Action
                module UnknownE020
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #8020..#81B8
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
                AND A
                JR NZ, @Action.UnknownE020.PointE047                            ; переход, если флаг Z сброшен


                LD HL, (#9B19)
                LD A, L
                SUB #77
                NEG
                JR Z, @Action.UnknownE020.PointE036                             ; переход, если флаг Z установлен


                INC L
                OR A
                JP P, @Action.UnknownE020.PointE036                             ; переход, если флаг Sign сброшен


                DEC L
                DEC L
PointE036:      LD A, H
                SUB #2B
                NEG
                JR Z, @Action.UnknownE020.PointE044                             ; переход, если флаг Z установлен


                INC H
                OR A
                JP P, @Action.UnknownE020.PointE044                             ; переход, если флаг Sign сброшен


                DEC H
                DEC H
PointE044:      LD (#9B19), HL
PointE047:      XOR A
                LD (#E021), A
                LD (#ED83), A
                LD HL, (#9B95)
                LD (#9B12), HL
                LD A, (#9B97)
                LD (#9B14), A
                CALL @Action.UnknownADB7.Entry
                LD A, (#9B01)
                CP #80
                JR NZ, @Action.UnknownE020.PointE065                            ; переход, если флаг Z сброшен


                INC A
PointE065:      LD (#CB3E), A
                LD A, (#9B03)
                CP #80
                JR NZ, @Action.UnknownE020.PointE070                            ; переход, если флаг Z сброшен


                INC A
PointE070:      LD (#CB8B), A
                LD A, (#9B05)
                CP #80
                JR NZ, @Action.UnknownE020.PointE07B                            ; переход, если флаг Z сброшен


                INC A
PointE07B:      LD (#CBD8), A
                LD A, (#9B07)
                CP #80
                JR NZ, @Action.UnknownE020.PointE086                            ; переход, если флаг Z сброшен


                INC A
PointE086:      LD (#CB54), A
                LD A, (#9B09)
                CP #80
                JR NZ, @Action.UnknownE020.PointE091                            ; переход, если флаг Z сброшен


                INC A
PointE091:      LD (#CBA1), A
                LD A, (#9B0B)
                CP #80
                JR NZ, @Action.UnknownE020.PointE09C                            ; переход, если флаг Z сброшен


                INC A
PointE09C:      LD (#CBEE), A
                LD A, (#9B0D)
                CP #80
                JR NZ, @Action.UnknownE020.PointE0A7                            ; переход, если флаг Z сброшен


                INC A
PointE0A7:      LD (#CB6F), A
                LD A, (#9B0F)
                CP #80
                JR NZ, @Action.UnknownE020.PointE0B2                            ; переход, если флаг Z сброшен


                INC A
PointE0B2:      LD (#CBBC), A
                LD A, (#9B11)
                CP #80
                JR NZ, @Action.UnknownE020.PointE0BD                            ; переход, если флаг Z сброшен


                INC A
PointE0BD:      LD (#CC09), A
                LD A, (#9B81)
                CP #01
                CALL NZ, @Action.Unknown6A6E.Entry                              ; вызов, если флаг Z сброшен
                CALL @Action.Unknown6B16.Entry
                LD HL, #0001
                LD (#9BA1), HL
                LD BC, #0040
                LD HL, #A100
                LD (#E4A7), SP
                JR @Action.UnknownE020.PointE0E4


PointE0DD:      LD A, L
                AND A
                JP M, @Action.UnknownE4A6.Entry                                 ; переход, если флаг Sign установлен


PointE0E2:      EXX
                ADD HL, BC
PointE0E4:      LD SP, HL
                EX DE, HL
                LD HL, #001B
                ADD HL, DE
                LD A, #80
                LD (HL), A
                EX DE, HL
                EXX
                POP HL
                CP H
                JR Z, @Action.UnknownE020.PointE0DD                             ; переход, если флаг Z установлен


                LD (#9B8F), HL
                LD A, H
                AND A
                JP P, @Action.UnknownE020.PointE0FD                             ; переход, если флаг Sign сброшен


                NEG
PointE0FD:      CP #70
                JR NC, @Action.UnknownE020.PointE0E2                            ; переход, если флаг Carry сброшен


                LD (#AF48), HL
                POP HL
                LD (#9B91), HL
                LD A, H
                AND A
                JP P, @Action.UnknownE020.PointE10F                             ; переход, если флаг Sign сброшен


                NEG
PointE10F:      CP #70
                JR NC, @Action.UnknownE020.PointE0E2                            ; переход, если флаг Carry сброшен


                LD (#AF56), HL
                POP HL
                LD (#9B93), HL
                LD A, H
                AND A
                JP P, @Action.UnknownE020.PointE121                             ; переход, если флаг Sign сброшен


                NEG
PointE121:      CP #70
                JR NC, @Action.UnknownE020.PointE0E2                            ; переход, если флаг Carry сброшен


                LD (#AF69), HL
                POP HL
                LD A, L
                LD (#9B8E), A
                LD A, H
                LD (#9B12), A
                POP HL
                LD (#9B13), HL
                LD A, (#9B14)
                LD B, A
                LD A, (#9B12)
                OR B
                LD A, #01
                JR Z, @Action.UnknownE020.PointE142                             ; переход, если флаг Z установлен


                XOR A
PointE142:      LD (#9B8D), A
                LD IY, #E14C
                JP @Action.UnknownAE73.PointAF43


                JP PE, @Action.UnknownE020.PointE0E2                            ; переход, если флаг P/V установлен


                EXX
                LD A, L
                EXX
                LD L, A
                EXX
                LD A, H
                EXX
                LD H, A
                LD DE, #0020
                ADD HL, DE
                LD SP, HL
                LD DE, (#D7A2)
                PUSH DE
                LD HL, (#D7C4)
                PUSH HL
                LD B, H
                LD HL, (#D9B6)
                PUSH HL
                LD A, H
                AND A
                JP P, @Action.UnknownE020.PointE171                             ; переход, если флаг Sign сброшен


                NEG
PointE171:      LD C, A
                LD A, D
                AND A
                JP P, @Action.UnknownE020.PointE179                             ; переход, если флаг Sign сброшен


                NEG
PointE179:      LD E, A
                LD A, B
                AND A
                JP P, @Action.UnknownE020.PointE181                             ; переход, если флаг Sign сброшен


                NEG
PointE181:      CP E
                JR NC, @Action.UnknownE020.PointE185                            ; переход, если флаг Carry сброшен


                LD A, E
PointE185:      CP C
                JR NC, @Action.UnknownE020.PointE189                            ; переход, если флаг Carry сброшен


                LD A, C
PointE189:      SRL A
                SUB #0F
                JR NC, @Action.UnknownE020.PointE194                            ; переход, если флаг Carry сброшен


                NEG
                JP @Action.UnknownE020.PointE195


PointE194:      XOR A
PointE195:      LD C, A
                LD A, (#ED83)
                CP C
                JR NC, @Action.UnknownE020.PointE19D                            ; переход, если флаг Carry сброшен


                LD A, C
PointE19D:      LD (#ED83), A
                LD A, D
                AND A
                JP M, @Action.UnknownE020.PointE0E2                             ; переход, если флаг Sign установлен


                CP #1F
                LD A, (#9B8E)
                JP P, @Action.UnknownE020.PointE1B2                             ; переход, если флаг Sign сброшен


                ADD A, #02
                LD (#9B8E), A
PointE1B2:      LD SP, (#E4A7)
                CALL @Action.UnknownAACC.Entry
                endmodule
                endmodule
