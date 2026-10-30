                module Controls
                module UnknownF188
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 23, файловые смещения #16AA..#16CC
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
Entry:          EXX
                AND #0F
                ADD A, #10
                LD L, A
                RES 0, L
                LD H, #00
                LD D, H
                LD E, L
                ADD HL, HL
                ADD HL, DE
                LD DE, #C600
                ADD HL, DE
                EX DE, HL
                EX AF, AF'
                LD H, #51
                EXX
                LD A, C
                EXX
                LD C, A
                SRL A
                LD L, A
                INC C
                CALL @Controls.UnknownEFF1.Entry
                EXX
                RET


                endmodule
                endmodule
