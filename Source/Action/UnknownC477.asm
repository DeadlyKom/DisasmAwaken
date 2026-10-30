                module Action
                module UnknownC477
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #6477..#6495
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
Entry:          LD BC, (#CF1B)
                LD HL, (#CF0B)
                OR A
                SBC HL, BC
                EX DE, HL
                LD BC, #0000
                LD HL, (#CF0D)
                OR A
                SBC HL, BC
                CALL @Action.UnknownC6F4.Entry
                LD (#CF37), DE
                LD (#CF39), HL
                RET


                endmodule
                endmodule
