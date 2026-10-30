                module Station
                module DrawItem44
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 44 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #17C7..#17DB
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
                LD (#7512), A
                XOR A
                LD (@TextWindow.Style), A
                LD HL, #DE8F
                JP @Station.PrintText.Entry


                endmodule
                endmodule
