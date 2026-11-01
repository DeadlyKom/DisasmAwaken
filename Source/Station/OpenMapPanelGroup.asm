                module Station
                module OpenMapPanelGroup
                ; Документация [фиксированный порядок одиннадцати ключей, алиасы и полные физические хвосты](../../Docs/MapPanelOpening.md)
                ; -----------------------------------------
                ; Подготовка группы из одиннадцати панелей карты с восстановлением геометрии и запросом обновления
                ; исходная запись 4, файловые смещения #1D70..#1DB6
                ; In:
                ;   BC сохраняемый контекст, входные HL, DE и AF отдельного параметра не задают
                ;   индексы в одиннадцати исходных рисователях подготовлены, их FInterfaceItem и Saved-поля доступны
                ;   список ограничен исходным маркером, хвосты сдвига 128 байтов доступны, действуют договоры RestoreItemBounds
                ;   банк станции 0 выбран, операнд RefreshPending доступен, обычный CPU-возврат доступен
                ; Out:
                ;   RefreshPending=1, последовательно восстановлены и перенесены ключи 21, 18, 19, 12, 13, 14, 15, 17, 16, 11, 20
                ;   HL содержит выбранный существующий либо исходный последний рисователь, DE равен ключу DrawVariantPanel, штатно 20
                ;   BC сохранён, AF содержит A=SavedHeight последней записи, F=A4
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2
                ;   X, Y, Width и Height выбранных записей восстановлены из Saved-полей, прочие поля сохранены
                ;   EventEnabled=0, список с физическим хвостом изменён, bitmap и активная страница сохранены
                ; Corrupt:
                ;   HL, DE, AF, RefreshPending, первые четыре поля выбранных FInterfaceItem, список и EventEnabled
                ; Note:
                ;   RestoreItemBounds принимает адрес рисователя, его изменяемое слово задаёт ключ, вход не является прямым индексом
                ;   при алиасе ключа сохраняется первый существующий адрес, исходный либо чужой C9 не включается автоматически
                ;   каждое найденное удаление сдвигает ровно 128 байтов, хвост за ограничителем является частью результата
                ;   это подготовка списка, немедленного рисования, банкового вызова и включения рисователей здесь нет
                ;   запрос позднее читает UpdateVariantPanel, его отложенный путь отдельно проверяет ActiveItemState.Active
                ; -----------------------------------------
                ; установка запроса позднего обновления панели вариантов до восстановления группы
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; подготовка сохранённой геометрии DrawItem21, позиция 1 из 11
                LD HL, @Station.DrawFlightButton.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawItem18, позиция 2 из 11
                LD HL, @Station.DrawContractButton.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawSystemInfoPanel, позиция 3 из 11
                LD HL, @Station.DrawSystemInfoPanel.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawStoredPointToggle, позиция 4 из 11
                LD HL, @Station.DrawStoredPointToggle.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawSecondaryPointToggle, позиция 5 из 11
                LD HL, @Station.DrawSecondaryPointToggle.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawItem14, позиция 6 из 11
                LD HL, @Station.DrawItem14.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawItem15, позиция 7 из 11
                LD HL, @Station.DrawItem15.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawItem17, позиция 8 из 11
                LD HL, @Station.DrawItem17.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawItem16, позиция 9 из 11
                LD HL, @Station.DrawItem16.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawMapPanel, позиция 10 из 11
                LD HL, @Station.DrawMapPanel.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; подготовка сохранённой геометрии DrawVariantPanel, позиция 11 из 11
                LD HL, @Station.DrawVariantPanel.Entry
                ; восстановление последней панели с возвратом сразу вызывающей стороне
                JP @Station.RestoreItemBounds.Entry

                endmodule
                endmodule
