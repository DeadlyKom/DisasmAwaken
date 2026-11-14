                module Station
                module ArrangeAllItems
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [выбор команды, фильтр закрытия и сохранение геометрии](../../Docs/MenuCommands.md)
; -----------------------------------------
; Восстановление геометрии всех элементов из сохранённых полей
; исходная запись 4, файловые смещения #47E0..#47E2
; In:
;   действует договор RestoreAllBounds для текущей таблицы FInterfaceItem
                ; Out:
                ;   HL сохранён, DE=FInterfaceItem, BC сохранён, AF=#8042
                ;   HL', DE', BC', AF' сохранены, IX адрес первого ограничителя с текущим X=#80, IY сохранён
                ;   I, IM и IFF сохранены, SP увеличен на два при чтении исходного адреса возврата
                ;   X, Y, Width и Height предшествующих записей заменены SavedX, SavedY, SavedWidth и SavedHeight
                ; Corrupt:
                ;   DE, AF, IX, R и четыре поля геометрии каждой обработанной записи
; Note:
;   хвостовой JP RestoreAllBounds не выполняет рисование и не меняет EventEnabled
; -----------------------------------------
                ; восстановление всей геометрии исходным RestoreAllBounds
Entry:          JP @Station.RestoreAllBounds.Entry

                endmodule
                endmodule
