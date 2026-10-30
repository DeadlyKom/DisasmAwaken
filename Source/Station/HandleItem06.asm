                module Station
                module HandleItem06
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 6 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #2067..#2070
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
Entry:          JP @Station.HandleItem06.Point7DBE


Point7DBE:      LD HL, #7DC5
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
