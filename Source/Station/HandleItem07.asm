                module Station
                module HandleItem07
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 7 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #2093..#209C
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
Entry:          JP @Station.HandleItem07.Point7DEA


Point7DEA:      LD HL, #7DF1
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
