                module Action
                module Unknown6F55
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #1192..#1253
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
                OR A
                LD C, #00
                LD (#6F59), A
                JR NZ, @Action.Unknown6F55.Point6F76                            ; переход, если флаг Z сброшен


                CP C
                JR NC, @Action.Unknown6F55.Point6F76                            ; переход, если флаг Carry сброшен


                CALL @Action.Unknown6172.Entry
                LD HL, #0088
                LD (#7693), HL
                LD HL, #0088
                LD (#A78F), HL
                LD A, #01
                LD (#669F), A
Point6F76:      XOR A
                LD (#6F56), A
                LD A, #00
                OR A
                LD A, #00
                LD (#6F7B), A
                JR NZ, @Action.Unknown6F55.Point6FAF                            ; переход, если флаг Z сброшен


                LD A, #C8
                LD (#7736), A
                LD (#7713), A
                LD A, #92
                RRCA
                LD (#6F8D), A
                JR NC, @Action.Unknown6F55.Point6FAF                            ; переход, если флаг Carry сброшен


                LD A, (#9B96)
                AND A
                JR Z, @Action.Unknown6F55.Point6FAF                             ; переход, если флаг Z установлен


                JP P, @Action.Unknown6F55.Point6FA6                             ; переход, если флаг Sign сброшен


                ADD A, #01
                JP M, @Action.Unknown6F55.Point6FAC                             ; переход, если флаг Sign установлен


                XOR A
                JP @Action.Unknown6F55.Point6FAC


Point6FA6:      SUB #01
                JP P, @Action.Unknown6F55.Point6FAC                             ; переход, если флаг Sign сброшен


                XOR A
Point6FAC:      LD (#9B96), A
Point6FAF:      LD A, #00
                OR A
                LD A, #00
                LD (#6FB0), A
                JR NZ, @Action.Unknown6F55.Point6FE4                            ; переход, если флаг Z сброшен


                LD A, #C8
                LD (#7759), A
                LD (#777C), A
                LD A, #92
                RRCA
                LD (#6FC2), A
                JR NC, @Action.Unknown6F55.Point6FE4                            ; переход, если флаг Carry сброшен


                LD A, (#9B95)
                AND A
                JR Z, @Action.Unknown6F55.Point6FE4                             ; переход, если флаг Z установлен


                JP P, @Action.Unknown6F55.Point6FDB                             ; переход, если флаг Sign сброшен


                ADD A, #01
                JP M, @Action.Unknown6F55.Point6FE1                             ; переход, если флаг Sign установлен


                XOR A
                JP @Action.Unknown6F55.Point6FE1


Point6FDB:      SUB #01
                JP P, @Action.Unknown6F55.Point6FE1                             ; переход, если флаг Sign сброшен


                XOR A
Point6FE1:      LD (#9B95), A
Point6FE4:      LD A, #00
                OR A
                LD A, #00
                LD (#6FE5), A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD A, #FA
                LD (#76CD), A
                LD (#76F0), A
                LD A, #92
                RRCA
                LD (#6FF6), A
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD A, (#9B97)
                AND A
                RET Z                                                           ; выход, если флаг Z установлен

                JP P, @Action.Unknown6F55.Point700D                             ; переход, если флаг Sign сброшен


                ADD A, #01
                JP M, @Action.Unknown6F55.Point7013                             ; переход, если флаг Sign установлен


                XOR A
                JP @Action.Unknown6F55.Point7013


Point700D:      SUB #01
                JP P, @Action.Unknown6F55.Point7013                             ; переход, если флаг Sign сброшен


                XOR A
Point7013:      LD (#9B97), A
                RET


                endmodule
                endmodule
