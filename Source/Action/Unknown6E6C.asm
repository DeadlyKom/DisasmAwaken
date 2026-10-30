                module Action
                module Unknown6E6C
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #10A9..#10E8
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
Entry:          CALL @Action.Unknown6EAC.Entry
                CALL @Action.Unknown6F1D.Entry
                LD A, (#CBD8)
                NOP
                NOP
                LD DE, (#A78F)
                LD IX, #6E82
                JP #D12C


                LD (#E5B3), HL
                LD A, (#CBEE)
                NOP
                NOP
                LD DE, (#A78F)
                LD IX, #6E95
                JP @Action.MultiplySignedScaled.Entry


                LD (#E5D2), HL
                LD A, (#CC09)
                NOP
                NOP
                LD DE, (#A78F)
                LD IX, #6EA8
                JP @Action.MultiplySignedScaled.Entry


                LD (#E5ED), HL
                RET


                endmodule
                endmodule
