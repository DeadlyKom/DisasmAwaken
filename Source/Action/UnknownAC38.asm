                module Action
                module UnknownAC38
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #4C38..#4C5C
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
Entry:          LD B, C
                LD L, (IX + #00)
                INC IX
                LD H, (IX + #00)
                INC IX
                RET


                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UnknownAC5D.Entry
                LD HL, #0000
                LD (#ECA9), HL
                LD (#ECF6), HL
                XOR A
                LD (#9B83), A
                LD (#9B82), A
                RET


                endmodule
                endmodule
