                module Station
                module DrawItem45
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик рисования станционного элемента из записи 45 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #1C01..#1C68
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
                LD HL, #CD82
                CALL @Station.PrintText.Entry
                PUSH HL
                CALL @Station.DescribeCurrentKey.Entry
                LD A, L
                DEC A
                LD HL, #CCF3
                CALL @Station.PrintAfterLF.Entry
                POP HL
                CALL @Station.PrintText.Entry
                PUSH HL
                LD HL, (#983F)
                LD DE, (#9841)
                LD A, #11
                CALL @Station.SelectRamBank.Entry
                CALL #E6AB
                LD HL, #630B
                CALL @Station.PrintText.Entry
                LD A, (#6320)
                ADD A, #04
                LD (#6320), A
                LD HL, (#983F)
                LD DE, (#9841)
                LD A, (#9843)
                CALL #C8C9
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                POP HL
                CALL @Station.PrintText.Entry
                PUSH HL
                CALL @Station.DescribeCurrentKey.Entry
                LD A, L
                ADD A, A
                ADD A, A
                ADD A, L
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
                POP HL
                CALL @Station.PrintText.Entry
                RET


                endmodule
                endmodule
