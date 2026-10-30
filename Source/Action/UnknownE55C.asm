                module Action
                module UnknownE55C
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #855C..#859E
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
Entry:          LD (#E605), SP
                LD A, (IX + #12)
                CP #14
                JR NZ, @Action.UnknownE55C.PointE58E                            ; переход, если флаг Z сброшен


                LD HL, (#E5B3)
                LD (#E68C), HL
                SRA H
                RR L
                LD (#E5B3), HL
                LD HL, (#E5D2)
                LD (#E692), HL
                SRA H
                RR L
                LD (#E5D2), HL
                LD HL, (#E5ED)
                LD (#E698), HL
                SRA H
                RR L
                LD (#E5ED), HL
PointE58E:      LD A, (IX + #06)
                CALL @Action.UnknownAACC.Entry
                LD A, #06
                SUB H
                LD HL, #00C8
                LD (#E59E), A
PointE59D:      JR @Action.UnknownE55C.PointE59D


                endmodule
                endmodule
