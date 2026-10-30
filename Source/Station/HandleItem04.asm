                module Station
                module HandleItem04
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 4 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #2029..#2032
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
Entry:          JP @Station.HandleItem04.Point7D80


Point7D80:      LD HL, #7D87
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
