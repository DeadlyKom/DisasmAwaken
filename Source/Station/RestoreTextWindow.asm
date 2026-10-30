                module Station
                module RestoreTextWindow
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [TextWindow.md](../../Docs/TextWindow.md)
; -----------------------------------------
; Восстановление девяти байтов текстового окна из изменяемых операндов LD A
; исходная запись 4, файловые смещения #4436..#4463
; In:
;   операнды восстановителя содержат последний снимок SaveTextWindow либо исходные байты игры
; Out:
;   восстановлены шесть байтов начала и размеров, Style, CursorX и CursorY, AF - A равен восстановленному CursorY, F сохранён
; Corrupt:
;   AF, только A
; Note:
;   восстановление не уничтожает снимок, повторный вызов снова применяет те же байты
;   HL, DE, BC, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   без предварительного SaveTextWindow применяются исходные значения операндов, это не стек контекстов
; -----------------------------------------
                ; восстановление младших байтов начала X и Y из последнего снимка
Entry:          LD A, #00
                LD (@TextWindow.OriginXLow), A
                LD A, #00
                LD (@TextWindow.OriginYLow), A
                ; восстановление знакового расширения начала окна
                LD A, #00
                LD (@TextWindow.OriginXHigh), A
                LD A, #00
                LD (@TextWindow.OriginYHigh), A
                ; восстановление пиксельной ширины и высоты
                LD A, #00
                LD (@TextWindow.Width), A
                LD A, #00
                LD (@TextWindow.Height), A
                ; восстановление байта режима текстового вывода
                LD A, #00
                LD (@TextWindow.Style), A
                ; восстановление относительного курсора X и Y
                LD A, #00
                LD (@TextWindow.CursorX), A
                LD A, #00
                LD (@TextWindow.CursorY), A
                RET

                endmodule
                endmodule
