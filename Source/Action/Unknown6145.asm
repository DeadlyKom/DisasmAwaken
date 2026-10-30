                module Action
                module Unknown6145
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0382..#03AE
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
Entry:          LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                LD A, #01
                LD (#669F), A
                LD (#666B), A
                LD (#664A), A
                LD (#668E), A
                LD (#667D), A
                LD (#665C), A
                CALL @Action.Unknown6649.Entry
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                LD HL, (#9BBF)
                LD DE, (#9BBD)
                LD B, #FF
                JP #F142


                endmodule
                endmodule
