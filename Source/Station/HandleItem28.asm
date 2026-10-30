                module Station
                module HandleItem28
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 28 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1CC7..#1CCF
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
Entry:          JP @Station.HandleItem28.Point7A1E


Point7A1E:      LD HL, #7A24
                CALL @Station.ActivateInterfaceCallback.Entry
                ; JP @Station.Unknown7A24.Entry, продолжение в Unknown7A24.asm

                endmodule
                endmodule
