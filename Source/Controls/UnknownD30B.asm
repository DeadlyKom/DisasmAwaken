                module Controls
                module UnknownD30B
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #130B..#131F
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
Entry:          PUSH HL
                LD H, #C3
                LD L, A
                LD E, (HL)
                INC H
                LD D, (HL)
                POP HL
                RET


PointD314:      CALL @Controls.UnknownD320.Entry
                CALL @Controls.UnknownD1F4.Entry
                CALL @Controls.UnknownD320.Entry
                JP @Controls.UnknownD1DF.Entry


                endmodule
                endmodule
