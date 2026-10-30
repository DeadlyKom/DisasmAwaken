                module Station
                module DrawItem25
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 25 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #0A8C..#0AE2
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
                XOR A
                LD (@TextWindow.Style), A
                LD A, #FF
                LD (#67D7), A
                LD A, #24
                LD (@TextStreamState.Column2X), A
                LD A, (#79DD)
                OR A
                JR Z, @Station.DrawItem25.Point6808                             ; переход, если флаг Z установлен


                LD A, (#6906)
                OR A
                LD A, (#9849)
                JR Z, @Station.DrawItem25.Point6806                             ; переход, если флаг Z установлен


                LD A, (#984A)
Point6806:      JR @Station.DrawItem25.Point681D


Point6808:      CALL @Station.DescribeCurrentKey.Entry
                DEC L
                LD A, L
                ADD A, A
                LD E, A
                LD D, #00
                LD HL, #94BC
                ADD HL, DE
                LD A, (#6906)
                OR A
                JR Z, @Station.DrawItem25.Point681C                             ; переход, если флаг Z установлен


                INC HL
Point681C:      LD A, (HL)
Point681D:      EX AF, AF'
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, (#79DD)
                LD H, A
                LD A, (#6906)
                CALL #E0C5
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                LD (#67D2), A
                RET


                endmodule
                endmodule
