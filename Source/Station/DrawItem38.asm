                module Station
                module DrawItem38
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 38 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #14D3..#14F7
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
                LD (@ScriptSelection.EquipmentRow), A
                CALL @Station.Unknown733F.Entry
                LD HL, #EE19
                CALL @Station.PrintText.Entry
                EX AF, AF'
                XOR A
                EX AF, AF'
                JP C, @Station.DrawItem38.Point7247                             ; переход, если флаг Carry установлен


                LD HL, (#71B9)
                CALL @Station.Unknown724C.Entry
Point7247:      EX AF, AF'
                LD (#7212), A
                RET


                endmodule
                endmodule
