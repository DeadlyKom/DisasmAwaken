                module Action
                module UnknownAE73
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4E73..#4F42
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
Entry:          LD BC, #0000
                EX DE, HL
                INC H
                DEC H
                JR Z, @Action.UnknownAE73.PointAEAA                             ; переход, если флаг Z установлен


                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEA8                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
PointAEA8:      RR L
PointAEAA:      LD H, #91
                LD A, (HL)
                INC H
                LD H, (HL)
                LD L, A
                ADD HL, BC
                EX DE, HL
                LD A, H
                RLA
                JR NC, @Action.UnknownAE73.PointAEBE                            ; переход, если флаг Carry сброшен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                SCF
PointAEBE:      EX AF, AF'
                LD BC, #0800
                INC H
                DEC H
                JR Z, @Action.UnknownAE73.PointAEF5                             ; переход, если флаг Z установлен


                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
                JR Z, @Action.UnknownAE73.PointAEF3                             ; переход, если флаг Z установлен


                RR L
                INC B
                SRA H
PointAEF3:      RR L
PointAEF5:      LD H, #91
                LD A, (HL)
                INC H
                LD H, (HL)
                LD L, A
                ADD HL, BC
                OR A
                SBC HL, DE
                JP M, @Action.UnknownAE73.PointAF22                             ; переход, если флаг Sign установлен


                LD A, H
                LD B, A
                LD H, #93
                LD L, (HL)
                LD H, #01
                SUB #08
                JR NC, @Action.UnknownAE73.PointAF27                            ; переход, если флаг Carry сброшен


                LD A, #07
                SUB B
                LD (#AF14), A
PointAF13:      JR NZ, @Action.UnknownAE73.PointAF13                            ; переход, если флаг Z сброшен


                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD L, H
                LD H, #00
                JP @Action.UnknownAE73.PointAF37


PointAF22:      LD HL, #0000
                AND A
                RET


PointAF27:      LD A, #0F
                SUB B
                RET C                                                           ; выход, если флаг Carry установлен

                LD (#AF2F), A
PointAF2E:      JR NZ, @Action.UnknownAE73.PointAF2E                            ; переход, если флаг Z сброшен


                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
PointAF37:      EX AF, AF'
                JR NC, @Action.UnknownAE73.PointAF41                            ; переход, если флаг Carry сброшен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
PointAF41:      AND A
                RET


                endmodule
                endmodule
