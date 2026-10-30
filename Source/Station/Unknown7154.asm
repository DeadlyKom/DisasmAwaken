                module Station
                module Unknown7154
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #1400..#141D
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
                LD (@TextWindow.Style), A
                LD A, #60
                LD (@TextStreamState.Column2X), A
                LD A, #72
                LD (@TextStreamState.Column3X), A
                LD A, #88
                LD (@TextStreamState.Column4X), A
                LD A, #9A
                LD (@TextStreamState.Column5X), A
                LD A, #B0
                LD (@TextStreamState.Column6X), A
                RET


                endmodule
                endmodule
