                module Action
                module UnknownC4B5
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #64B5..#64D3
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
Entry:          LD BC, #0000
                LD HL, (#CF0B)
                OR A
                SBC HL, BC
                EX DE, HL
                LD BC, (#CF1D)
                LD HL, (#CF0D)
                OR A
                SBC HL, BC
                CALL @Action.UnknownC6F4.Entry
                LD (#CF2F), DE
                LD (#CF31), HL
                RET


                endmodule
                endmodule
