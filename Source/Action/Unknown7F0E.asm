                module Action
                module Unknown7F0E
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #214B..#21B2
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
Entry:          LD DE, #0000
                LD HL, #0000
                CALL @Action.Unknown7F76.Entry
                LD A, H
                AND #80
                OR D
                OR E
                JR Z, @Action.Unknown7F0E.Point7F21                             ; переход, если флаг Z установлен


                LD HL, #7F00
Point7F21:      PUSH HL
                LD DE, #0000
                LD HL, #0000
                CALL @Action.Unknown7F76.Entry
                LD A, H
                AND #80
                OR D
                OR E
                JR Z, @Action.Unknown7F0E.Point7F35                             ; переход, если флаг Z установлен


                LD HL, #7F00
Point7F35:      PUSH HL
                LD DE, #0000
                LD HL, #0000
                CALL @Action.Unknown7F76.Entry
                LD A, H
                AND #80
                OR D
                OR E
                JR Z, @Action.Unknown7F0E.Point7F49                             ; переход, если флаг Z установлен


                LD HL, #7F00
Point7F49:      LD B, H
                LD C, L
                POP DE
                POP HL
                LD A, (#7F0F)
                OR A
                JP P, @Action.Unknown7F0E.Point7F5B                             ; переход, если флаг Sign сброшен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point7F5B:      LD A, (#7F23)
                OR A
                JP P, @Action.Unknown7F0E.Point7F69                             ; переход, если флаг Sign сброшен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
Point7F69:      LD A, (#7F37)
                OR A
                RET P                                                           ; выход, если флаг Sign сброшен

                LD A, C
                CPL
                LD C, A
                LD A, B
                CPL
                LD B, A
                INC BC
                RET


                endmodule
                endmodule
