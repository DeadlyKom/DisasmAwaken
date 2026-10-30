                module Station
                module SaveTextWindow
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [TextWindow.md](../../Docs/TextWindow.md)
; -----------------------------------------
; Сохранение девяти байтов текстового окна в операндах одноместного восстановителя
; исходная запись 4, файловые смещения #43FF..#4435
; In:
;   TextWindow - текущие шесть байтов начала и размеров, два байта курсора и байт Style
;   операнды RestoreTextWindow доступны для записи
; Out:
;   девять байтов сохранены в соответствующих операндах RestoreTextWindow, AF - A равен исходному TextWindow.Style, F сохранён
; Corrupt:
;   AF, только A
; Note:
;   снимок один на все вызовы, повторное сохранение заменяет предыдущий снимок, вложенные сохранения не поддерживаются
;   HL, DE, BC, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   физический снимок находится в разнесённых операндах LD A, не является непрерывной структурой данных
; -----------------------------------------
                ; сохранение начала X и Y в младших изменяемых операндах восстановителя
Entry:          LD A, (@TextWindow.OriginXLow)
                LD (@TextWindow.SavedXLow), A
                LD A, (@TextWindow.OriginYLow)
                LD (@TextWindow.SavedYLow), A
                ; сохранение знакового расширения начала текстового окна
                LD A, (@TextWindow.OriginXHigh)
                LD (@TextWindow.SavedXHigh), A
                LD A, (@TextWindow.OriginYHigh)
                LD (@TextWindow.SavedYHigh), A
                ; сохранение пиксельных размеров текстового окна
                LD A, (@TextWindow.Width)
                LD (@TextWindow.SavedWidth), A
                LD A, (@TextWindow.Height)
                LD (@TextWindow.SavedHeight), A
                ; сохранение относительного курсора до переключения окна
                LD A, (@TextWindow.CursorX)
                LD (@TextWindow.SavedCursorX), A
                LD A, (@TextWindow.CursorY)
                LD (@TextWindow.SavedCursorY), A
                ; сохранение режима текста, назначение отдельных разрядов ещё не установлено
                LD A, (@TextWindow.Style)
                LD (@TextWindow.SavedStyle), A
                RET

                endmodule
                endmodule
