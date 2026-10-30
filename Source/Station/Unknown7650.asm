                module Station
                module Unknown7650
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #18FC..#1917
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
Entry:          EX DE, HL
                LD HL, #0800
                LD (#6320), HL
                LD HL, #DF3C
                PUSH DE
                LD A, E
                CALL @Station.PrintAfterCR.Entry
                LD A, #08
                LD (#6321), A
                POP HL
                LD BC, #9736
                ADD HL, BC
                JP @Station.Unknown6BBE.Point6BD7


                endmodule
                endmodule
