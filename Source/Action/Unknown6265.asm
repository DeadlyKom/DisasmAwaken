                module Action
                module Unknown6265
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #04A2..#04F1
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
Entry:          CALL @Action.UnknownAD5A.Entry
                LD A, (IX + #08)
                LD D, A
                SUB B
                LD E, A
                JP P, @Action.Unknown6265.Point6273                             ; переход, если флаг Sign сброшен


                NEG
Point6273:      LD L, A
                CP #02
                JR C, @Action.Unknown6265.Point628E                             ; переход, если флаг Carry установлен


                LD A, (IX + #25)
Point627B:      CP L
                JR C, @Action.Unknown6265.Point6284                             ; переход, если флаг Carry установлен


                JR Z, @Action.Unknown6265.Point6284                             ; переход, если флаг Z установлен


                RRA
                JP @Action.Unknown6265.Point627B


Point6284:      BIT 7, E
                JR NZ, @Action.Unknown6265.Point628A                            ; переход, если флаг Z сброшен


                NEG
Point628A:      ADD A, D
                LD (IX + #08), A
Point628E:      LD A, (IX + #09)
                LD D, A
                SUB C
                LD E, A
                JP P, @Action.Unknown6265.Point6299                             ; переход, если флаг Sign сброшен


                NEG
Point6299:      LD H, A
                CP (IX + #25)
                RET C                                                           ; выход, если флаг Carry установлен

                LD A, (IX + #25)
Point62A1:      CP H
                JR Z, @Action.Unknown6265.Point62AA                             ; переход, если флаг Z установлен


                JR C, @Action.Unknown6265.Point62AA                             ; переход, если флаг Carry установлен


                RRA
                JP @Action.Unknown6265.Point62A1


Point62AA:      BIT 7, E
                JR NZ, @Action.Unknown6265.Point62B0                            ; переход, если флаг Z сброшен


                NEG
Point62B0:      ADD A, D
                LD (IX + #09), A
                RET


                endmodule
                endmodule
