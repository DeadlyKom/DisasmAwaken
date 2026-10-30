                module Action
                module Unknown6D38
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0F75..#100D
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
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, #00
                DEC A
                JR NZ, @Action.Unknown6D38.Point6D45                            ; переход, если флаг Z сброшен


                XOR A
                LD (#6D39), A
Point6D45:      LD (#6D3D), A
                LD IX, #A783
                LD DE, #0012
Point6D4F:      ADD IX, DE
                LD A, (IX + #07)
                AND A
                RET M                                                           ; выход, если флаг Sign установлен

                JR Z, @Action.Unknown6D38.Point6D4F                             ; переход, если флаг Z установлен


                DEC (IX + #07)
                LD L, (IX + #04)
                LD H, (IX + #05)
                LD (#AF69), HL
                LD BC, (#E5ED)
                OR A
                SBC HL, BC
                LD (IX + #04), L
                LD (IX + #05), H
                LD L, (IX + #00)
                LD H, (IX + #01)
                LD (#AF48), HL
                LD BC, (#E5B3)
                OR A
                SBC HL, BC
                LD (IX + #00), L
                LD (IX + #01), H
                LD L, (IX + #02)
                LD H, (IX + #03)
                LD (#AF56), HL
                LD BC, (#E5D2)
                OR A
                SBC HL, BC
                LD (IX + #02), L
                LD (IX + #03), H
                EXX
                LD E, (IX + #08)
                LD D, (IX + #09)
                DEC (IX + #0C)
                JR NZ, @Action.Unknown6D38.Point6DB8                            ; переход, если флаг Z сброшен


                LD A, (IX + #0D)
                LD (IX + #0C), A
                LD L, (IX + #0A)
                LD H, (IX + #0B)
                JP @Action.Unknown6D38.Point6DBF


Point6DB8:      LD L, (IX + #0E)
                LD H, (IX + #0F)
                ADD HL, DE
Point6DBF:      LD (IX + #08), L
                LD (IX + #09), H
                EXX
                LD (#6DD2), SP
                LD IY, #6DD1
                JP @Action.UnknownAE73.PointAF43


                endmodule
                endmodule
