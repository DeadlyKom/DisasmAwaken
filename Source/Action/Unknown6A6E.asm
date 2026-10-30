                module Action
                module Unknown6A6E
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0CAB..#0CE9
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
Entry:          LD HL, #9B6F
                LD DE, #9B1E
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LD HL, (#9B1F)
                LD (#AF48), HL
                LD HL, (#9B22)
                LD (#AF56), HL
                LD HL, (#9B25)
                LD (#AF69), HL
                LD (#6AAE), SP
                XOR A
                LD (#9B1E), A
                LD (#9B21), A
                LD (#9B24), A
                LD IY, #6AAD
                JP @Action.UnknownAE73.PointAF43


                endmodule
                endmodule
