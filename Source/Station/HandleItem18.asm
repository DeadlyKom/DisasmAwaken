                module Station
                module HandleItem18
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 18 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1F68..#1F71
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
Entry:          JP @Station.HandleItem18.Point7CBF


Point7CBF:      LD HL, #7CC6
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
