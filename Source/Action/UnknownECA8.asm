                module Action
                module UnknownECA8
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #8CA8..#8D8E
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
Entry:          LD HL, #0000
                LD A, H
                OR A
                JR Z, @Action.UnknownECA8.PointECF5                             ; переход, если флаг Z установлен


                LD BC, #FFFD
                XOR A
                OUT (C), A
                LD B, #BF
                OUTI
                LD B, #FF
                LD A, #01
                OUT (C), A
                LD B, #BF
                OUTI
                LD B, #FF
                LD A, #07
                OUT (C), A
                IN A, (C)
                AND #F6
                OR (HL)
                LD B, #BF
                OUT (C), A
                INC HL
                LD A, #08
                LD B, #FF
                OUT (C), A
                LD B, #BF
                OUTI
                LD (#ECA9), HL
                LD A, (HL)
                OR A
                JR NZ, @Action.UnknownECA8.PointECF5                            ; переход, если флаг Z сброшен


                LD (#ECAA), A
                LD B, #FF
                LD A, #07
                OUT (C), A
                IN A, (C)
                OR #09
                LD B, #BF
                OUT (C), A
PointECF5:      LD HL, #0000
                LD A, H
                OR A
                JR Z, @Action.UnknownECA8.PointED46                             ; переход, если флаг Z установлен


                LD BC, #FFFD
                LD A, #02
                OUT (C), A
                LD B, #BF
                OUTI
                LD B, #FF
                LD A, #03
                OUT (C), A
                LD B, #BF
                OUTI
                LD B, #FF
                LD A, #07
                OUT (C), A
                IN A, (C)
                AND #ED
                LD B, A
                LD A, (HL)
                RLCA
                OR B
                LD B, #BF
                OUT (C), A
                INC HL
                LD A, #09
                LD B, #FF
                OUT (C), A
                LD B, #BF
                OUTI
                LD (#ECF6), HL
                LD A, (HL)
                OR A
                JR NZ, @Action.UnknownECA8.PointED46                            ; переход, если флаг Z сброшен


                LD (#ECF7), A
                LD B, #FF
                LD A, #07
                OUT (C), A
                IN A, (C)
                OR #12
                LD B, #BF
                OUT (C), A
PointED46:      LD C, #FD
                LD B, #FF
                LD A, #05
                OUT (C), A
                LD B, #BF
                LD A, #0C
                OUT (C), A
                LD B, #FF
                LD A, #07
                OUT (C), A
                LD A, R
                CP #20
                JR C, @Action.UnknownECA8.PointED62                             ; переход, если флаг Carry установлен


                LD A, #20
PointED62:      AND #20
                LD L, A
                IN A, (C)
                AND #DB
                OR L
                LD B, #BF
                OUT (C), A
                LD A, #06
                LD B, #FF
                OUT (C), A
                LD B, #BF
                LD A, #05
                OUT (C), A
                LD A, #0A
                LD B, #FF
                OUT (C), A
                LD B, #BF
                LD A, #00
                SRL A
                CP #04
                JR NC, @Action.UnknownECA8.PointED8C                            ; переход, если флаг Carry сброшен


                LD A, #04
PointED8C:      OUT (C), A
                RET


                endmodule
                endmodule
