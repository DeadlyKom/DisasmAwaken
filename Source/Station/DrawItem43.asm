                module Station
                module DrawItem43
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 43 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #173E..#1752
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
                LD (@PanelHoverState.ToPositionRow), A
                XOR A
                LD (@TextWindow.Style), A
                LD HL, #DE53
                JP @Station.PrintText.Entry


                endmodule
                endmodule
