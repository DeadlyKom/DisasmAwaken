                module Station
                module Unknown733F
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #15EB..#160A
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
                LD A, #74
                LD (@TextStreamState.Column2X), A
                LD A, #86
                LD (@TextStreamState.Column3X), A
                LD A, #9C
                LD (@TextStreamState.Column4X), A
                LD A, #AE
                LD (@TextStreamState.Column5X), A
                CALL @Station.DescribeCurrentKey.Entry
                LD A, L
                LD (#72DD), A
                RET


                endmodule
                endmodule
