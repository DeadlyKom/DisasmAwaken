                module Action
                module Unknown6CEF
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0F2C..#0F3C
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
Entry:          EX AF, AF'
                LD E, A
                LD A, #13
                CALL @Action.SelectMemoryPage.Entry
                LD A, E
                LD IY, #A783
                LD DE, #6D00
                PUSH DE
                JP (HL)


                endmodule
                endmodule
