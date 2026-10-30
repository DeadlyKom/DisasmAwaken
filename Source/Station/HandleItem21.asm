                module Station
                module HandleItem21
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 21 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1DF2..#1DFB
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
Entry:          JP @Station.HandleItem21.Point7B49


Point7B49:      LD HL, #7B50
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
