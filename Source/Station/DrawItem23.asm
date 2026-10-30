                module Station
                module DrawItem23
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 23 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0C54..#0C63
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
Entry:          LD HL, #0000
                CALL @Station.DrawCaptionItem.Entry
                CALL @Station.Unknown69B8.Entry
                LD HL, (#699D)
                CALL @Station.Unknown69CF.Entry
                RET


                endmodule
                endmodule
