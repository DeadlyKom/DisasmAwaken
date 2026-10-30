                module Controls
                module UnknownC870
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #0870..#0881
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
Entry:          LD HL, #400F
                EXX
                LD HL, #8000
                LD A, #08
                CALL @Controls.UnknownC882.Entry
                EXX
                LD H, #48
                EXX
                LD A, #04
                ; JP @Controls.UnknownC882.Entry, продолжение в UnknownC882.asm

                endmodule
                endmodule
