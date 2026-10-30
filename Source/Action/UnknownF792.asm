                module Action
                module UnknownF792
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #9792..#97BE
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
Entry:          LD A, (IX + #0B)
                CP #1A
                LD C, #0A
                JR NZ, @Action.UnknownF792.PointF7B5                            ; переход, если флаг Z сброшен


                LD C, #0A
                BIT 3, (IX + #0C)
                JR Z, @Action.UnknownF792.PointF7B5                             ; переход, если флаг Z установлен


                LD A, (#9C1A)
                INC A
                LD C, #1E
                JR NZ, @Action.UnknownF792.PointF7B5                            ; переход, если флаг Z сброшен


                LD A, (#9C1B)
                INC A
                LD C, #3C
                JR NZ, @Action.UnknownF792.PointF7B5                            ; переход, если флаг Z сброшен


                LD C, #14
PointF7B5:      LD A, (IX + #13)
                SUB C
                JP NC, @Action.UnknownF7C6.PointF7E6                            ; переход, если флаг Carry сброшен


                CALL @Action.UnknownEA29.Entry
                endmodule
                endmodule
