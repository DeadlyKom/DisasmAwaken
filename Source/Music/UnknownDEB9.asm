                module Music
                module UnknownDEB9
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #03B9..#0401
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
Entry:          XOR A
                LD L, A
                LD H, A
                LD (#E198), HL
                JR @Music.UnknownDEB9.PointDEEA


                LD (#E0F9), A
                LD (#E13D), A
                LD (#E154), A
                LD (#E17C), A
                LD (#E19F), A
                LD (#E1D7), A
                LD (#E16C), HL
                CPL
                LD (#E0EE), A
                LD A, #00
                LD (#E1BB), A
                LD HL, #0000
                LD (#E0F5), HL
                LD A, #10
                LD (#E110), A
PointDEEA:      LD A, #00
                LD (#E12C), A
                JR @Music.UnknownDEB9.PointDF00


                XOR A
                LD (#E17C), A
                LD HL, #0000
                LD (#E178), HL
                LD A, #00
                LD (#E136), A
PointDF00:      JR @Music.UnknownDF1E.Entry


                endmodule
                endmodule
