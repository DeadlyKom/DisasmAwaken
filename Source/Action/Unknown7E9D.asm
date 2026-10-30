                module Action
                module Unknown7E9D
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #20DA..#20F3
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
Entry:          LD IY, #9B27
                LD A, (#688B)
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                LD B, A
                LD DE, #000C
Point7EAA:      CALL @Action.Unknown6A29.Entry
                JR C, @Action.Unknown7EB7.Entry                                 ; переход, если флаг Carry установлен


                ADD IY, DE
                DJNZ @Action.Unknown7E9D.Point7EAA

                LD IY, #9B27
                ; JP @Action.Unknown7EB7.Entry, продолжение в Unknown7EB7.asm

                endmodule
                endmodule
