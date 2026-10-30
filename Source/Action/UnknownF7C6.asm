                module Action
                module UnknownF7C6
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #97C6..#9865
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
Entry:          LD A, (IX + #12)
                CP #12
                JP Z, @Action.UnknownF075.Entry                                 ; переход, если флаг Z установлен


                CP #10
                JR NC, @Action.UnknownF7C6.PointF843                            ; переход, если флаг Carry сброшен


                LD A, (IX + #0A)
                CP #07
                JP Z, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Z установлен


                CP #06
                JP Z, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Z установлен


                LD (IX + #0A), #05
                JP @Action.UnknownF7C6.PointF843


PointF7E6:      LD (IX + #13), A
                LD A, (IX + #12)
                CP #10
                JP NC, @Action.UnknownF7C6.PointF843                            ; переход, если флаг Carry сброшен


                LD A, (IX + #0A)
                CP #02
                JP NZ, @Action.UnknownF7C6.PointF808                            ; переход, если флаг Z сброшен


                LD C, (IX + #0B)
                INC C
                JR Z, @Action.UnknownF7C6.PointF812                             ; переход, если флаг Z установлен


                LD A, R
                CP #0A
                JR C, @Action.UnknownF7C6.PointF812                             ; переход, если флаг Carry установлен


                JP @Action.UnknownF7C6.PointF843


PointF808:      CP #04
                JP C, @Action.UnknownF7C6.PointF812                             ; переход, если флаг Carry установлен


                CP #0A
                JP C, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Carry установлен


PointF812:      LD A, (IX + #12)
                AND #0F
                CP #03
                LD C, #70
                JP Z, @Action.UnknownF7C6.PointF82C                             ; переход, если флаг Z установлен


                CP #00
                LD C, #75
                JP Z, @Action.UnknownF7C6.PointF82C                             ; переход, если флаг Z установлен


                CP #01
                LD C, #50
                JP Z, @Action.UnknownF7C6.PointF82C                             ; переход, если флаг Z установлен


PointF82C:      LD A, (IX + #0A)
                CP #07
                JR Z, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Z установлен


                CP #06
                JR Z, @Action.UnknownF7C6.PointF843                             ; переход, если флаг Z установлен


                LD A, R
                CP C
                LD A, #02
                JR C, @Action.UnknownF7C6.PointF840                             ; переход, если флаг Carry установлен


                LD A, #05
PointF840:      LD (IX + #0A), A
PointF843:      LD (IX + #0C), #00
                LD A, (IX + #0A)
                SLA A
                LD L, A
                LD H, #00
                LD DE, #EF50
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                PUSH IX
                LD DE, #F85E
                PUSH DE
                JP (HL)


                POP IX
                CALL @Action.UnknownE55C.Entry
                JP @Action.UpdateObjects.PointF735


                endmodule
                endmodule
