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
;   HL и BC сохранены, DE=FInterfaceItem, AF=#8042, IX ограничитель X=#80
;   X..Height восстановлены из SavedX..SavedHeight, альтернативные регистры, IY, I и IFF сохранены
; Corrupt:
;   DE, AF, IX
; Note:
;   хвостовой JP RestoreAllBounds не выполняет рисование и не меняет EventEnabled
; -----------------------------------------
                ; восстановление всей геометрии исходным RestoreAllBounds
Entry:          JP #CB7F

                endmodule
                endmodule
