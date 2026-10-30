                module Station
                module DrawItem34
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 34 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #131D..#1341
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
                CALL @Station.Unknown7154.Entry
                LD A, #FF
                LD (#7068), A
                LD HL, #EBF3
                CALL @Station.PrintText.Entry
                EX AF, AF'
                XOR A
                EX AF, AF'
                JP C, @Station.DrawItem34.Point7091                             ; переход, если флаг Carry установлен


                LD HL, (#7026)
                CALL @Station.Unknown7096.Entry
Point7091:      EX AF, AF'
                LD (#7063), A
                RET


                endmodule
                endmodule
