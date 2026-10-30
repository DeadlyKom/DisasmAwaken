                module Station
                module HandleItem29
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 29 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1D07..#1D0F
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
Entry:          JP @Station.HandleItem29.Point7A5E


Point7A5E:      LD HL, #7A64
                CALL @Station.ActivateInterfaceCallback.Entry
                ; JP @Station.Unknown7A64.Entry, продолжение в Unknown7A64.asm

                endmodule
                endmodule
