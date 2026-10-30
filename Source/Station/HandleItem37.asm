                module Station
                module HandleItem37
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 37 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1DBD..#1DC5
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
Entry:          JP @Station.HandleItem37.Point7B14


Point7B14:      LD HL, #7B1A
                CALL @Station.ActivateInterfaceCallback.Entry
                ; JP @Station.Unknown7B1A.Entry, продолжение в Unknown7B1A.asm

                endmodule
                endmodule
