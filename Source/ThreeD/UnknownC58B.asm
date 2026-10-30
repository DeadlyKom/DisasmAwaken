                module ThreeD
                module UnknownC58B
; Документация [ThreeD](../../Docs/FunctionDetails/ThreeD.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 19, файловые смещения #058B..#05E3
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
Entry:          LD A, (#CF2F)
                EX AF, AF'
                LD A, (#CF30)
                LD HL, (#CF1B)
                LD DE, (#CF0B)
                OR A
                SBC HL, DE
                EX DE, HL
                LD HL, (#CF31)
                CALL @ThreeD.UnknownC88C.Entry
                LD DE, (#CF0D)
                ADD HL, DE
                LD A, H
                AND A
                JP M, @ThreeD.UnknownC58B.PointC5C3                             ; переход, если флаг Sign установлен


                LD A, L
                AND A
                JP P, @ThreeD.UnknownC58B.PointC5D3                             ; переход, если флаг Sign сброшен


                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), #00
                INC L
                LD (HL), #5F
                INC L
                LD A, L
                LD (#9BA3), A
                RET


PointC5C3:      LD A, (#9BA3)
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


PointC5D3:      LD D, L
                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), #00
                INC L
                LD (HL), D
                INC L
                LD A, L
                LD (#9BA3), A
                RET


                endmodule
                endmodule
