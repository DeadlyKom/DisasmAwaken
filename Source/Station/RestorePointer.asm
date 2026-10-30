                module Station
                module RestorePointer
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [указатель и сохранение фона](../../Docs/Pointer.md)
; -----------------------------------------
; Восстановление двух сохранённых байтов каждой видимой строки указателя
; исходная запись 4, файловые смещения #07F3..#0820
; In:
;   при RestoredFlag=0 BackgroundAddr и VisibleRows=1..8 описывают сохранённые строки по BackgroundBase
; Out:
;   при ненулевом RestoredFlag A=его значение, F=AND(A), HL, DE и BC сохранены
;   при нулевом RestoredFlag фон восстановлен, флаг становится 1, HL=BackgroundBase+2*VisibleRows
;   DE - адрес строки после восстановленных, B=0, C=255-2*VisibleRows, AF результат перехода строки
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   все альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   сохраняются и восстанавливаются два байта строки, независимо от однобайтового правого отсечения
;   ноль VisibleRows не обрабатывается отдельно и запустил бы 256 итераций DJNZ
;   используется тот же изменяемый операнд VisibleRows, который исполняется как LD B в DrawPointer
; -----------------------------------------
                ; чтение RestoredFlag непосредственно из изменяемого операнда LD A
Entry:          LD A, #00
                ; проверка отсутствия активного рисунка по ненулевому состоянию фона
                AND A
                RET NZ                                                          ; выход, если фон уже восстановлен, экран не менять

                ; пометка фона восстановленным перед копированием его пикселей
                INC A
                LD (@PointerState.RestoredFlag), A
                ; восстановление экранного адреса из самоподменяемого слова BackgroundAddr
                LD DE, #0000
                LD HL, @PointerConst.BackgroundBase
                LD C, #FF
                ; чтение числа строк из того же операнда VisibleRows, который исполняется рисователем
                LD A, (@PointerState.VisibleRows)
                LD B, A
                ; восстановление двух сохранённых байтов строки, независимо от правого отсечения рисунка
RestoreRow:     LDI
                LDI
                DEC DE
                DEC DE
                ; расчёт следующей экранной строки с исходным чередованием адресов
                INC D
                LD A, D
                ; проверка границы восьми пиксельных строк знакоместа
                AND @PointerConst.Low3Mask
                JP NZ, @Station.RestorePointer.RestoreNext                      ; переход, если граница знакоместа ещё не достигнута, продолжить восстановление

                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Station.RestorePointer.RestoreNext                       ; переход, если перенос младшего адреса уже перевёл в следующую треть

                LD A, D
                SUB @PointerConst.CellHeight
                LD D, A
RestoreNext:    DJNZ @Station.RestorePointer.RestoreRow

                RET

                endmodule
                endmodule
