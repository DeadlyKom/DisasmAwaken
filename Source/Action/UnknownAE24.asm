                module Action
                module UnknownAE24
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4E24..#4E72
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
Entry:          LD A, D
                XOR H
                PUSH AF
                PUSH DE
                BIT 7, D
                JR Z, @Action.UnknownAE24.PointAE33                             ; переход, если флаг Z установлен


                LD A, E
                CPL
                LD E, A
                LD A, D
                CPL
                LD D, A
                INC DE
PointAE33:      CALL @Action.UnknownAE73.Entry
                POP BC
                JR C, @Action.UnknownAE24.PointAE6C                             ; переход, если флаг Carry установлен


                BIT 7, H
                JR Z, @Action.UnknownAE24.PointAE44                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
PointAE44:      LD A, L
                SRL H
                RRA
                SRL H
                RRA
                SRL H
                RRA
                SRL H
                RRA
                LD L, A
                LD A, H
                AND A
                JP NZ, @Action.UnknownAE24.PointAE6C                            ; переход, если флаг Z сброшен


                POP AF
                LD H, #9A
                LD A, (HL)
                JP P, @Action.UnknownAE24.PointAE66                             ; переход, если флаг Sign сброшен


                ADD A, #40
                BIT 7, B
                RET NZ                                                          ; выход, если флаг Z сброшен

                ADD A, #80
                RET


PointAE66:      BIT 7, B
                RET Z                                                           ; выход, если флаг Z установлен

                ADD A, #80
                RET


PointAE6C:      POP AF
                LD A, #40
                RET P                                                           ; выход, если флаг Sign сброшен

                LD A, #C0
                RET


                endmodule
                endmodule
