                module Music
                module UnknownDF47
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 10, файловые смещения #0447..#046C
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
Entry:          LD A, #00
                LD (#DC0D), A
                OR A
                JR Z, @Music.UnknownDF47.PointDF61                              ; переход, если флаг Z установлен


                LD HL, #0000
                LD (#E2F1), HL
                XOR A
                LD L, A
                LD H, A
                LD (#DF48), A
                LD (#E2EE), HL
                LD (#E2FA), A
PointDF61:      LD A, #03
                LD (#E37D), A
                LD A, #00
                LD (#DC06), A
                JR @Music.AdvancePatternA.Entry


                endmodule
                endmodule
