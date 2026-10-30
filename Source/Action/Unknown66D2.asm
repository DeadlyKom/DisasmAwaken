                module Action
                module Unknown66D2
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #090F..#09BC
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
Entry:          LD HL, (#9B78)
                LD A, (#9B7A)
                LD DE, (#E5B3)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown66D2.Point66E3                             ; переход, если флаг Z установлен


                DEC C
Point66E3:      OR A
                SBC HL, DE
                LD (#9B78), HL
                SBC A, C
                RET PE                                                          ; выход, если флаг P/V установлен

                LD (#9B7A), A
                LD HL, (#9B7B)
                LD A, (#9B7D)
                LD DE, (#E5D2)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown66D2.Point66FF                             ; переход, если флаг Z установлен


                DEC C
Point66FF:      OR A
                SBC HL, DE
                LD (#9B7B), HL
                SBC A, C
                RET PE                                                          ; выход, если флаг P/V установлен

                LD (#9B7D), A
                LD HL, (#9B7E)
                LD DE, (#E5ED)
                LD A, (#9B80)
                BIT 7, D
                LD C, #00
                JR Z, @Action.Unknown66D2.Point671B                             ; переход, если флаг Z установлен


                DEC C
Point671B:      OR A
                SBC HL, DE
                LD (#9B7E), HL
                SBC A, C
                RET PE                                                          ; выход, если флаг P/V установлен

                LD (#9B80), A
                RET


Point6727:      LD A, (#9B81)
                CP #02
                RET Z                                                           ; выход, если флаг Z установлен

                LD A, #01
                LD (#9B81), A
                LD HL, #1527
                LD (#EBF6), HL
                LD A, #13
                LD (#EBF8), A
                LD A, #FF
                LD (#7B6B), A
Point6742:      CALL #EBD4
                LD A, H
                CP #87
                JP NZ, @Action.Unknown6780.Point688A                            ; переход, если флаг Z сброшен


                LD A, L
                CP #46
                JP NZ, @Action.Unknown6780.Point688A                            ; переход, если флаг Z сброшен


                LD A, #02
                LD (#9B81), A
                LD HL, #6000
                LD (#9B70), HL
                LD (#9B73), HL
                LD (#9B76), HL
                JP @Action.Unknown6780.Point688A


Point6765:      LD HL, (#9B70)
                LD BC, #FFD0
                ADD HL, BC
                LD (#9B70), HL
                LD HL, (#9B76)
                ADD HL, BC
                LD (#9B76), HL
                LD HL, (#9B73)
                ADD HL, BC
                LD (#9B73), HL
                JP @Action.Unknown6780.Point679B


                endmodule
                endmodule
