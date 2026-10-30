                module Controls
                module UnknownCEFA
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0EFA..#0F0A
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
Entry:          LD (#D240), DE
                XOR A
                LD (#CEF9), A
                CALL @Controls.UnknownD95F.Entry
                AND A
                RET Z                                                           ; выход, если флаг Z установлен

                CALL @Controls.UnknownD21A.Entry
                RET


                endmodule
                endmodule
