                module Station
                module DrawItem10
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 10 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1136..#1144
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
                LD A, #00
                LD HL, #CE19
                CALL @Station.JustifyAfterLF.Entry
                RET


                endmodule
                endmodule
