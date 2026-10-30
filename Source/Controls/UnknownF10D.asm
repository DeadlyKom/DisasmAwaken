                module Controls
                module UnknownF10D
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #162F..#1663
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
Entry:          LD A, #80
                RRCA
                LD (#F10E), A
                RET NC                                                          ; выход, если флаг Carry сброшен

                LD BC, #0000
                LD HL, (#9BBF)
                LD A, L
                ADD A, #01
                DAA
                LD L, A
                LD A, H
                JR NC, @Controls.UnknownF10D.PointF124                          ; переход, если флаг Carry сброшен


                SET 0, B
PointF124:      ADC A, C
                DAA
                LD H, A
                LD DE, (#9BBD)
                LD A, E
                JR NC, @Controls.UnknownF10D.PointF130                          ; переход, если флаг Carry сброшен


                SET 1, B
PointF130:      ADC A, C
                DAA
                LD E, A
                LD A, D
                JR NC, @Controls.UnknownF10D.PointF138                          ; переход, если флаг Carry сброшен


                SET 2, B
PointF138:      ADC A, C
                DAA
                LD D, A
                LD (#9BBF), HL
                LD (#9BBD), DE
                ; JP @Controls.UnknownF142.Entry, продолжение в UnknownF142.asm

                endmodule
                endmodule
