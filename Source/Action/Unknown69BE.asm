                module Action
                module Unknown69BE
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0BFB..#0C65
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
Entry:          LD A, (#688B)
                OR A
                LD L, #7F
                RET Z                                                           ; выход, если флаг Z установлен

                PUSH IY
                LD B, A
                LD IY, #9B27
                LD DE, #000C
Point69CF:      CALL @Action.Unknown6A29.Entry
                JR C, @Action.Unknown69BE.Point69DD                             ; переход, если флаг Carry установлен


                ADD IY, DE
                DJNZ @Action.Unknown69BE.Point69CF

                LD L, #7F
                POP IY
                RET


Point69DD:      LD E, (IY + #01)
                LD D, (IY + #02)
                BIT 7, (IY + #03)
                JR Z, @Action.Unknown69BE.Point69EF                             ; переход, если флаг Z установлен


                LD A, D
                CPL
                LD D, A
                LD A, E
                CPL
                LD E, A
Point69EF:      LD L, D
                LD H, E
                LD E, (IY + #05)
                LD D, (IY + #06)
                BIT 7, (IY + #07)
                JR Z, @Action.Unknown69BE.Point6A03                             ; переход, если флаг Z установлен


                LD A, D
                CPL
                LD D, A
                LD A, E
                CPL
                LD E, A
Point6A03:      LD A, D
                CP L
                JR C, @Action.Unknown69BE.Point6A09                             ; переход, если флаг Carry установлен


                LD L, A
                LD H, E
Point6A09:      LD E, (IY + #09)
                LD D, (IY + #0A)
                BIT 7, (IY + #0B)
                JR Z, @Action.Unknown69BE.Point6A1B                             ; переход, если флаг Z установлен


                LD A, D
                CPL
                LD D, A
                LD A, E
                CPL
                LD E, A
Point6A1B:      LD A, D
                CP L
                JR C, @Action.Unknown69BE.Point6A21                             ; переход, если флаг Carry установлен


                LD L, A
                LD H, E
Point6A21:      LD A, (#688B)
                SUB B
                LD E, A
                POP IY
                RET


                endmodule
                endmodule
