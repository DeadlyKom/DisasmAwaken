                module Station
                module HandleItem36
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 36 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1DD7..#1DDF
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
Entry:          JP @Station.HandleItem36.Point7B2E


Point7B2E:      LD HL, #7B34
                CALL @Station.ActivateInterfaceCallback.Entry
                ; JP @Station.Unknown7B34.Entry, продолжение в Unknown7B34.asm

                endmodule
                endmodule
