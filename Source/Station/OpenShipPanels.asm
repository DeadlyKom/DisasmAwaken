                module Station
                module OpenShipPanels
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [продажа выбранного груза, отложенные callback и порядок групп панелей](../../Docs/ControlPanelGroups.md)
                ; -----------------------------------------
                ; Сброс выбора и восстановление шести корабельных панелей в исходном порядке
                ; исходная запись 4, файловые смещения #209D..#20C4
                ; In:
                ;   условия ResetShipPanelSelection, актуальные индексы рисователей и сохранённые границы всех шести панелей
                ;   каждый исходный рисователь содержит актуальный индекс по адресу Entry+1, список и FInterfaceItem допустимы по договору RestoreItemBounds
                ;   имеется место в списке рисования, сохранённые поля геометрии подготовлены
                ; Out:
                ;   границы восстановлены последовательно для элементов 30, 29, 28, 25, 27, 26, EventEnabled каждого обработанного элемента равен нулю
                ;   HL - сохранённый в списке рисователь последнего ключа либо переданный исходный адрес при отсутствии ключа
                ;   DE - индекс последнего рисователя, BC сохранён, AF - A последняя SavedHeight, F=A4
                ;   все альтернативные и индексные регистры сохранены, SP обычного возврата равен входному SP+2
                ;   перед восстановлением выполнен ResetShipPanelSelection с A=0, его изменения режима, рамок и банка 4 сохранены
                ; Corrupt:
                ;   HL, DE, AF
                ; Note:
                ;   каждый RestoreItemBounds переносит первое совпадение индекса в конец списка, существующий адрес-алиас сохраняется
                ;   немедленного рисования нет, C9 отключённого рисователя не заменяется на 21, индекс по Entry+1 читается и при C9
                ;   последний RestoreItemBounds вызван хвостовым JP, его RET использует исходный адрес возврата
                ;   ResetShipPanelSelection вызывается до обхода списка, режим и рамки меняются даже у отключённых рисователей
                ; -----------------------------------------
                ; выбор селектора 0 и сброс корабельного списка до восстановления границ
Entry:          XOR A
                CALL @Station.ResetShipPanelSelection.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawItem30.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawPurchaseModeButton.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawSaleModeButton.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawModelListPanel.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawModelDescriptionPanel.Entry
                CALL @Station.RestoreItemBounds.Entry
                ; восстановление следующей панели в исходной последовательности 30, 29, 28, 25, 27, 26
                LD HL, @Station.DrawShipPreview.Entry
                JP @Station.RestoreItemBounds.Entry

                endmodule
                endmodule
