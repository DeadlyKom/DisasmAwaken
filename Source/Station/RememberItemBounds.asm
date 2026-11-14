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
                ;   HL сохранён, DE=FInterfaceItem, BC сохранён, AF=#8042
                ;   HL', DE', BC', AF' сохранены, IX адрес первого ограничителя с текущим X=#80, IY сохранён
                ;   I, IM и IFF сохранены, SP увеличен на два при чтении исходного адреса возврата
                ;   SavedX, SavedY, SavedWidth и SavedHeight предшествующих записей заменены X, Y, Width и Height
                ; Corrupt:
                ;   DE, AF, IX, R и четыре поля геометрии каждой обработанной записи
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
