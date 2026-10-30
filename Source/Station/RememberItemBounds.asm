                module Station
                module RememberItemBounds
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [выбор команды, фильтр закрытия и сохранение геометрии](../../Docs/MenuCommands.md)
; -----------------------------------------
; Копирование текущей геометрии всех записей в SavedX..SavedHeight
; исходная запись 4, файловые смещения #47B7..#47DF
; In:
;   StationState.Items содержит достижимый X=#80, все предшествующие физические записи доступны для записи
; Out:
;   HL и BC сохранены, DE=FInterfaceItem, AF=#8042
;   IX адрес первого ограничителя X=#80, текущие X..Height скопированы в SavedX..SavedHeight
;   альтернативные регистры, IY, I и IFF сохранены, SP восстановлен
; Corrupt:
;   DE, AF, IX
; Note:
;   ограничитель проверяется по текущему X, геометрия и флаги не проверяются
;   остальные двенадцать байтов записи не меняются, ограничитель и последующий хвост нетронуты
;   SavedX=#80 допустим как данные, исходный текущий X=#80 уже завершает проход
; -----------------------------------------
                ; поиск всех физических элементов от начала StationState.Items
Entry:          LD IX, @StationState.Items
                ; выбор исходного шестнадцатибайтового шага записи
                LD DE, FInterfaceItem
                ; проверка текущего X на ограничитель таблицы элементов
NextItem:       LD A, (IX + FInterfaceItem.X)
                CP @InterfaceTable.EndX
                RET Z                                                           ; выход, если текущий X равен #80, ограничитель не копировать

                ; сохранение текущих четырёх полей геометрии в SavedX..SavedHeight
                LD A, (IX + FInterfaceItem.X)
                LD (IX + FInterfaceItem.SavedX), A
                LD A, (IX + FInterfaceItem.Y)
                LD (IX + FInterfaceItem.SavedY), A
                LD A, (IX + FInterfaceItem.Width)
                LD (IX + FInterfaceItem.SavedWidth), A
                LD A, (IX + FInterfaceItem.Height)
                LD (IX + FInterfaceItem.SavedHeight), A
                ; переход к следующему физическому FInterfaceItem
                ADD IX, DE
                JR @Station.RememberItemBounds.NextItem

                endmodule
                endmodule
