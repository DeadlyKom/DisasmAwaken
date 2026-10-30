                module Controls
                module UnknownECA2
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #11C4..#1214
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
                OR L
                JR NZ, @Controls.UnknownECA2.PointECD2                          ; переход, если флаг Z сброшен


                LD HL, #0000
                INC HL
                INC HL
PointECAE:      LD (#ECAA), HL
                LD A, (HL)
                CP #02
                JR C, @Controls.UnknownECA2.PointECC9                           ; переход, если флаг Carry установлен


                LD (HL), #01
                LD D, A
                INC HL
                LD E, (HL)
                JR NZ, @Controls.UnknownECA2.PointECD1                          ; переход, если флаг Z сброшен


                LD A, E
                CALL @Controls.UnknownECF3.Entry
                LD A, (#EFD6)
                INC A
                LD (#EFD6), A
                RET


PointECC9:      OR A
                RET NZ                                                          ; выход, если флаг Z сброшен

                LD HL, #EC80
                JP @Controls.UnknownECA2.PointECAE


PointECD1:      EX DE, HL
PointECD2:      LD A, (HL)
                INC HL
                LD (#ECA3), HL
                CP #0A
                JR Z, @Controls.UnknownECA2.PointECE2                           ; переход, если флаг Z установлен


                CP #0D
                JR Z, @Controls.UnknownECA2.PointECE9                           ; переход, если флаг Z установлен


                JP @Controls.UnknownEFC4.Entry


PointECE2:      LD HL, #0000
                LD (#ECA3), HL
                RET


PointECE9:      XOR A
                LD (#EFD6), A
                CALL @Controls.UnknownED28.Entry
                JP @Controls.UnknownECA2.Entry


                endmodule
                endmodule
