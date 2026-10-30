                module Station
                module DrawItem39
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 39 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0D62..#0D71
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
                CALL @Station.Unknown6AC6.Entry
                LD HL, (#6AA4)
                CALL @Station.Unknown6ADE.Entry
                RET


                endmodule
                endmodule
