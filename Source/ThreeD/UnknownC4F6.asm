                module ThreeD
                module UnknownC4F6
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 19, файловые смещения #04F6..#053C
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
Entry:          LD A, (#CF37)
                EX AF, AF'
                LD A, (#CF38)
                LD HL, (#CF1D)
                LD DE, (#CF0D)
                OR A
                SBC HL, DE
                EX DE, HL
                LD HL, (#CF39)
                CALL @ThreeD.UnknownC88C.Entry
                LD DE, (#CF0B)
                ADD HL, DE
                LD A, H
                AND A
                JR Z, @ThreeD.UnknownC4F6.PointC52C                             ; переход, если флаг Z установлен


                JP P, @ThreeD.UnknownC4F6.PointC52A                             ; переход, если флаг Sign сброшен


                LD A, (#9BA3)
                LD L, A
                LD H, #90
                XOR A
                LD (HL), A
                INC L
                LD (HL), A
                INC L
                LD A, L
                LD (#9BA3), A
                RET


PointC52A:      LD L, #FF
PointC52C:      LD E, L
                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), E
                INC L
                LD (HL), #00
                INC L
                LD A, L
                LD (#9BA3), A
                RET


                endmodule
                endmodule
