                module Station
                module RestoreItemBounds
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [список указателей и сохранённая геометрия](../../Docs/InterfaceBounds.md)
; -----------------------------------------
; Перенос обработчика в конец списка и восстановление геометрии его элемента
; исходная запись 4, файловые смещения #6BA9..#6BDF
; In:
;   HL - обёртка с читаемым шестнадцатибитным индексом в Handler+1, Handler+2
;   индекс соответствует читаемой и записываемой FInterfaceItem, действует договор MoveItemToTail
;   страница станционного кода и её таблица выбраны, стек имеет место для FRestoreBoundsFrame
; Out:
;   HL - выбранный существующий либо входной обработчик после MoveItemToTail, DE - индекс из входной обёртки
;   BC сохранён, AF - A=SavedHeight, F=#A4, IX сохранён
;   X..Height выбранной записи восстановлены из SavedX..SavedHeight, InterfaceState.EventEnabled=0
; Corrupt:
;   HL, DE, AF
; Note:
;   альтернативные регистры, IY, I и IFF сохраняются, SP восстанавливается
;   до восстановления геометрии вызывается MoveItemToTail с его физическим сдвигом 128 байтов
;   код входной обёртки не исполняется, её непосредственный индекс читается даже при отключённом RET
;   FRestoreBoundsFrame хранит SavedIX, SavedBC, SelectedHandler и ReturnAddress
;   геометрия не проверяется на видимость и не регистрируется в карте владельцев
; -----------------------------------------
                ; сброс операнда EventEnabled в MainLoop, запрос перестроения и запрет событий до него
Entry:          XOR A
                LD (@InterfaceState.EventEnabled), A
                ; чтение индекса из двух байтов входной обёртки без исполнения её кода
                INC HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                DEC HL
                DEC HL
                CALL @Station.MoveItemToTail.Entry
                ; создание FRestoreBoundsFrame.SelectedHandler из результата MoveItemToTail
                PUSH HL
                ; сохранение FRestoreBoundsFrame.SavedBC
                PUSH BC
                ; сохранение FRestoreBoundsFrame.SavedIX
                PUSH IX
                ; перенос прочитанного индекса из DE в HL для адресации записи
                LD H, D
                LD L, E
                ; выбор начала записи по нулевому смещению
                XOR A
                CALL @Station.GetItemField.Entry
                ; установка IX на физическую запись без изменения её индекса в DE
                PUSH HL
                POP IX
                ; восстановление четырёх полей геометрии, последний LD A оставляет SavedHeight в A
                LD A, (IX + FInterfaceItem.SavedX)
                LD (IX + FInterfaceItem.X), A
                LD A, (IX + FInterfaceItem.SavedY)
                LD (IX + FInterfaceItem.Y), A
                LD A, (IX + FInterfaceItem.SavedWidth)
                LD (IX + FInterfaceItem.Width), A
                LD A, (IX + FInterfaceItem.SavedHeight)
                LD (IX + FInterfaceItem.Height), A
                ; снятие FRestoreBoundsFrame с восстановлением IX, BC и выбранного обработчика HL
                POP IX
                POP BC
                POP HL
                RET

                endmodule
                endmodule
