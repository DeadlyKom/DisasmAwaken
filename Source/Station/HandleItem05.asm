                module Station
                module HandleItem05
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 5 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #204B..#2054
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
Entry:          JP @Station.HandleItem05.Point7DA2


Point7DA2:      LD HL, #7DA9
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
