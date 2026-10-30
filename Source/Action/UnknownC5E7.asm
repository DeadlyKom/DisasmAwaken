                module Action
                module UnknownC5E7
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #65E7..#6640
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
Entry:          LD A, (#CF2B)
                EX AF, AF'
                LD A, (#CF2C)
                LD HL, (#CF1B)
                LD DE, (#CF0B)
                OR A
                SBC HL, DE
                EX DE, HL
                LD HL, (#CF2D)
                CALL @Action.UnknownC88C.Entry
                LD DE, (#CF0D)
                ADD HL, DE
                LD A, H
                AND A
                JP M, @Action.UnknownC5E7.PointC61F                             ; переход, если флаг Sign установлен


                LD A, L
                AND A
                JP P, @Action.UnknownC5E7.PointC630                             ; переход, если флаг Sign сброшен


                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), #FF
                INC L
                LD (HL), #5F
                INC L
                LD A, L
                LD (#9BA3), A
                RET


PointC61F:      LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), #FF
                INC L
                LD (HL), #00
                INC L
                LD A, L
                LD (#9BA3), A
                RET


PointC630:      LD D, L
                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), #FF
                INC L
                LD (HL), D
                INC L
                LD A, L
                LD (#9BA3), A
                RET


                endmodule
                endmodule
