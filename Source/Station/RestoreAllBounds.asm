                module Station
                module RestoreAllBounds
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [список указателей и сохранённая геометрия](../../Docs/InterfaceBounds.md)
; -----------------------------------------
; Восстановление первых четырёх полей каждой записи из SavedX..SavedHeight до X=#80
; исходная запись 4, файловые смещения #6B7F..#6BA8
; In:
;   StationState.Items указывает таблицу FInterfaceItem с достижимым X=#80 до выхода физической таблицы из допустимой памяти
;   окно станционного банка и поля X..Height доступны для записи
; Out:
;   HL сохранён, DE=FInterfaceItem, BC сохранён, AF=#8042
;   IX - адрес первой записи, чей прежний X равен #80, она и последующий хвост не меняются
;   у предшествующих записей X, Y, Width, Height заменены SavedX, SavedY, SavedWidth, SavedHeight
; Corrupt:
;   DE, AF, IX
; Note:
;   альтернативные регистры, IY, I и IFF сохраняются, SP восстанавливается
;   контролируется только текущее X, не Flags и не число 46
;   SavedX=#80 копируется как обычный байт, но может стать ограничителем при следующем вызове
;   геометрия не проверяется и не отсекается, остальные двенадцать байтов каждой записи сохраняются
; -----------------------------------------
                ; выбор начала таблицы физических FInterfaceItem
Entry:          LD IX, @StationState.Items
                LD DE, FInterfaceItem
                ; проверка текущего X на маркер конца таблицы
NextItem:       LD A, (IX + FInterfaceItem.X)
                CP @InterfaceTable.EndX
                RET Z                                                           ; выход, если текущий X равен #80, эта запись остаётся нетронутой

                ; восстановление X, Y, Width, Height из четырёх сохранённых физических полей
                LD A, (IX + FInterfaceItem.SavedX)
                LD (IX + FInterfaceItem.X), A
                LD A, (IX + FInterfaceItem.SavedY)
                LD (IX + FInterfaceItem.Y), A
                LD A, (IX + FInterfaceItem.SavedWidth)
                LD (IX + FInterfaceItem.Width), A
                LD A, (IX + FInterfaceItem.SavedHeight)
                LD (IX + FInterfaceItem.Height), A
                ; переход к следующей записи с исходным шагом FInterfaceItem
                ADD IX, DE
                JP @Station.RestoreAllBounds.NextItem

                endmodule
                endmodule
