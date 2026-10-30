                module Action
                module Unknown6F1D
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #115A..#118A
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
Entry:          LD IX, #9D4C
                LD DE, #7015
                LD L, #1C
                LD C, #FE
Point6F28:      DEC L
                JR Z, @Action.Unknown6F55.Entry                                 ; переход, если флаг Z установлен


                LD B, (IX + #00)
                INC IX
                INC IX
                INC DE
                INC DE
                IN A, (C)
                AND (IX - #01)
                JR NZ, @Action.Unknown6F1D.Point6F28                            ; переход, если флаг Z сброшен


                PUSH HL
                PUSH DE
                PUSH BC
                PUSH IX
                LD A, (DE)
                LD L, A
                INC DE
                LD A, (DE)
                LD H, A
                LD A, (#A85F)
                AND A
                LD DE, #6F4E
                PUSH DE
                JP (HL)


                endmodule
                endmodule
