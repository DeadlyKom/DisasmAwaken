                module Action
                module UnknownB0E9
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #50E9..#516E
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
                AND A
                JR Z, @Action.UnknownB0E9.PointB120                             ; переход, если флаг Z установлен


                LD L, A
                LD H, #C0
                LD A, (HL)
                INC H
                LD C, A
                CPL
                EX AF, AF'
                LD B, #FF
                INC BC
                SLA C
                RL B
                DEC BC
                LD A, (HL)
                INC H
                LD H, (HL)
                LD L, A
                EX AF, AF'
                ADD HL, DE
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                DEC BC
                DEC BC
                INC A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                DEC BC
                DEC BC
                INC A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                DEC BC
                DEC BC
                INC A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                DEC BC
                DEC BC
                INC A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                DEC BC
                DEC BC
                INC A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                RET


PointB120:      EX DE, HL
                LD BC, #FFFF
                XOR A
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                DEC BC
                DEC BC
                ADD HL, BC
                RET NC                                                          ; выход, если флаг Carry сброшен

                INC A
                RET


                endmodule
                endmodule
