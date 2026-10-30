                module Action
                module UpdateObjects
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Обход записей по #40 байт от #A100 с ограничителем #80 и обновление состояний
; исходная запись 17, файловые смещения #9729..#9774
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
Entry:          LD IX, #A0C0
                JR @Action.UpdateObjects.PointF735


PointF72F:      LD A, (IX + #00)
                CP #80
                RET Z                                                           ; выход, если флаг Z установлен

PointF735:      LD DE, #0040
                ADD IX, DE
                LD A, (IX + #01)
                CP #80
                JP Z, @Action.UpdateObjects.PointF72F                           ; переход, если флаг Z установлен


                LD A, (IX + #12)
                CP #10
                JP NC, @Action.UpdateObjects.PointF759                          ; переход, если флаг Carry сброшен


                LD A, (IX + #22)
                DEC A
                LD H, A
                LD A, (IX + #13)
                CP H
                JR NC, @Action.UpdateObjects.PointF759                          ; переход, если флаг Carry сброшен


                INC A
                LD (IX + #13), A
PointF759:      LD A, (IX + #0C)
                AND A
                JP Z, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Z установлен


                BIT 1, A
                JP NZ, @Action.UnknownF7C6.Entry                                ; переход, если флаг Z сброшен


                LD A, (IX + #12)
                CP #12
                JR NZ, @Action.UnknownF792.Entry                                ; переход, если флаг Z сброшен


                LD A, (IX + #0B)
                LD (IX + #0D), A
                CALL @Action.Unknown62CF.Entry
                endmodule
                endmodule
