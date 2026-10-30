                module Station
                module HandleItem33
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 33 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #4A33..#4A3C
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
Entry:          JP @Station.HandleItem33.PointAA36


PointAA36:      LD HL, #AA3D
                CALL @Station.ActivateInterfaceCallback.Entry
                RET


                endmodule
                endmodule
