                module Controls
                module UnknownD1A2
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #11A2..#11B5
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
Entry:          PUSH AF
                EXX
                LD HL, #0000
                LD D, H
                LD B, #FF
                EXX
                XOR A
                LD (#D18B), A
                LD A, (#D18C)
                AND A
                JP @Controls.UnknownD833.Entry


                endmodule
                endmodule
