                module Action
                module UnknownC540
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #6540..#6587
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
Entry:          LD A, (#CF33)
                EX AF, AF'
                LD A, (#CF34)
                LD HL, (#CF1D)
                LD DE, (#CF0D)
                OR A
                SBC HL, DE
                EX DE, HL
                LD HL, (#CF35)
                CALL @Action.UnknownC88C.Entry
                LD DE, (#CF0B)
                ADD HL, DE
                LD A, H
                AND A
                JR Z, @Action.UnknownC540.PointC577                             ; переход, если флаг Z установлен


                JP P, @Action.UnknownC540.PointC575                             ; переход, если флаг Sign сброшен


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


PointC575:      LD L, #FF
PointC577:      LD E, L
                LD A, (#9BA3)
                LD L, A
                LD H, #90
                LD (HL), E
                INC L
                LD (HL), #5F
                INC L
                LD A, L
                LD (#9BA3), A
                RET


                endmodule
                endmodule
