                module Station
                module DrawItem41
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 41 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0E51..#0E69
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
                LD A, #FF
                LD (#6B95), A
                CALL @Station.Unknown6C00.Entry
                LD HL, (#6B23)
                CALL @Station.Unknown6BBE.Entry
                EX AF, AF'
                LD (#6B90), A
                RET


                endmodule
                endmodule
