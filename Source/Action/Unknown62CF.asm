                module Action
                module Unknown62CF
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #050C..#054D
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
Entry:          LD B, #00
                LD HL, #A0C1
                LD DE, #0040
                JP @Action.Unknown62CF.Point62E1


Point62DA:      DEC L
                LD A, (HL)
                CP #80
                JR Z, @Action.Unknown62CF.Point630D                             ; переход, если флаг Z установлен


                INC L
Point62E1:      ADD HL, DE
                LD A, (HL)
                CP #80
                JR Z, @Action.Unknown62CF.Point62DA                             ; переход, если флаг Z установлен


                LD A, L
                LD C, A
                ADD A, #11
                LD L, A
                LD A, (HL)
                CP #03
                LD L, C
                JR NZ, @Action.Unknown62CF.Point62E1                            ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #09
                LD L, A
                LD A, (HL)
                CP #02
                LD L, C
                JR NZ, @Action.Unknown62CF.Point62E1                            ; переход, если флаг Z сброшен


                LD A, L
                ADD A, #0A
                LD L, A
                LD A, (HL)
                CP (IX + #0D)
                LD L, C
                JR NZ, @Action.Unknown62CF.Point62E1                            ; переход, если флаг Z сброшен


                INC B
                LD A, B
                CP #02
                JR C, @Action.Unknown62CF.Point62E1                             ; переход, если флаг Carry установлен


Point630D:      LD A, B
                CP #02
                RET


                endmodule
                endmodule
