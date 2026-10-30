                module Station
                module HandleItem35
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 35 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #2005..#200E
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
Entry:          JP @Station.HandleItem35.Point7D5C


Point7D5C:      LD HL, #7D63
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
