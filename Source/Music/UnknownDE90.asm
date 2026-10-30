                module Music
                module UnknownDE90
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #0390..#03A4
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
Entry:          JR @Music.UnknownDE90.PointDEA3


                LD A, E
                LD (#DE90), A
                LD A, #00
                LD (#E0E9), A
                LD (#E0D7), A
                LD A, #00
                LD (#E0E5), A
PointDEA3:      JR @Music.UnknownDEAE.Entry


                endmodule
                endmodule
