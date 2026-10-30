                module Station
                module HandleItem30
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 30 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1C69..#1C72
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
Entry:          JP @Station.HandleItem30.Point79C0


Point79C0:      LD HL, #79C7
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
