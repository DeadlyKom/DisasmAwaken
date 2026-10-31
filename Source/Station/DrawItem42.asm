                module Station
                module DrawItem42
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 42 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #18E3..#18FB
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
                LD (@PanelHoverState.GameSettingsRow), A
                CALL @Station.Unknown766C.Entry
                LD HL, (#75D3)
                CALL @Station.Unknown7650.Entry
                EX AF, AF'
                LD (#7622), A
                RET


                endmodule
                endmodule
