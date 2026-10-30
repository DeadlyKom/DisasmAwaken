                module Station
                module DrawItem22
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 22 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0D07..#0D29
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
                LD (#6A52), A
                CALL @Station.Unknown6A7E.Entry
                LD HL, (#6A15)
                LD A, #17
                CALL @Station.SelectRamBank.Entry
                CALL #DB5B
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                LD (#6A4D), A
                RET


                endmodule
                endmodule
