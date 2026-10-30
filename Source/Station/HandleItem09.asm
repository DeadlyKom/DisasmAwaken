                module Station
                module HandleItem09
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 9 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1D34..#1D3D
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
Entry:          JP @Station.HandleItem09.Point7A8B


Point7A8B:      LD HL, #7A92
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
