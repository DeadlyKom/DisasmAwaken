                module Station
                module Unknown7AC4
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1D70..#1DB6
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
Entry:          LD A, #01
                LD (#78D7), A
                LD HL, #7B51
                CALL @Station.RestoreItemBounds.Entry
                LD HL, #7CF8
                CALL #CBA9
                LD HL, #768F
                CALL #CBA9
                LD HL, #7BA8
                CALL #CBA9
                LD HL, #7C1E
                CALL #CBA9
                LD HL, #7C7E
                CALL #CBA9
                LD HL, #7CB6
                CALL #CBA9
                LD HL, #7D24
                CALL #CBA9
                LD HL, #7D53
                CALL #CBA9
                LD HL, #6DA8
                CALL #CBA9
                LD HL, #788C
                JP #CBA9


                endmodule
                endmodule
