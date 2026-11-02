                module Controls
                module UnknownD314
                ; Документация [частичный разбор контура](../../Docs/ControlsCircleInterior.md)
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1314..#131F
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
Entry:          CALL @Controls.BuildCircleSpan.Entry
                CALL @Controls.UnknownD1F4.Entry
                CALL @Controls.BuildCircleSpan.Entry
                JP @Controls.UnknownD1DF.Entry


                endmodule
                endmodule
