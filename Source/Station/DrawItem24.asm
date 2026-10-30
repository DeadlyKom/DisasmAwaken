                module Station
                module DrawItem24
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 24 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1080..#10BC
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
                LD A, #01
                LD (@TextWindow.Style), A
                LD HL, (#983F)
                LD DE, #4B37
                XOR A
                SBC HL, DE
                JP NZ, @Station.Unknown6E76.Entry                               ; переход, если флаг Z сброшен


                LD HL, (#9841)
                LD DE, #4E25
                XOR A
                SBC HL, DE
                JP NZ, @Station.Unknown6E76.Entry                               ; переход, если флаг Z сброшен


                LD A, (#98A0)
                CP #FE
                JP Z, @Station.DrawItem24.Point6E02                             ; переход, если флаг Z установлен


                JP @Station.Unknown6E76.Entry


Point6E02:      DI
                LD HL, #6E11
                LD DE, #4000
                LD BC, #0200
                LDIR
                JP #4000


                endmodule
                endmodule
