                module Station
                module DropShipDetailPanels
                ; Документация [единица после RepaintAndFlag, строка FF, сброс описания, пять ключей и физический хвост удаления](../../Docs/ShipModelActions.md)
                ; -----------------------------------------
                ; Отключение периодического просмотра и последовательное удаление пяти связанных панелей
                ; исходная запись 4, файловые смещения #0A2C..#0A54
                ; In:
                ;   HL заменяется адресом EmptyCallback, DE последовательно получает пять изменяемых индексов, BC сохраняется
                ;   AF задаёт начальный Carry для пустого списка, список и хвосты доступны по договору DropItemDraw
                ;   DrawItemState.Index30, PreviewIndex, ModelDescriptionState.ItemIndex, Index28 и Index29 содержат читаемые слова
                ; Out:
                ;   HL=EmptyCallback.Entry, DE последний прочитанный Index29, BC сохранён
                ;   AF=0044 при найденном последнем ключе, иначе A=0,F=42 OR Carry последнего сравнения, пустой список сохраняет Carry
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены
                ;   MenuCommandState.PeriodicCall=EmptyCallback.Entry, пять первых совпадений ключей удаляются в исходном порядке
                ;   EventEnabled становится нулём при любом найденном ключе, при отсутствии всех ключей сохраняется
                ;   bitmap, карта владельцев и геометрия здесь не перерисовываются, SP после возврата входному+2
                ; Corrupt:
                ;   HL, DE, AF, список с физическими хвостами, PeriodicCall и EventEnabled
                ; Note:
                ;   порядок ключей соответствует панелям 30, 26, 27, 28, 29 в штатной конфигурации, сами индексы не зашиты в инструкциях
                ;   текущая панель списка 25 этим входом не удаляется, в действии перед ним её условно удаляет CloseMenuOnRow
                ;   каждое совпадение переносит ровно 128 байтов и может затронуть данные после ограничителя
                ;   равные ключи выполняют несколько последовательных удалений, временный C9 чужого адреса не мешает сравнению индекса
                ; -----------------------------------------
                ; отключение будущего периодического просмотра до удаления панелей
Entry:          LD HL, @Station.EmptyCallback.Entry
                LD (@MenuCommandState.PeriodicCall), HL
                ; чтение и удаление первого ключа группы, в штатной таблице панель 30
                LD DE, (@DrawItemState.Index30)
                CALL @Station.DropItemDraw.Entry
                ; чтение и удаление ключа корабельного просмотра
                LD DE, (@ShipPanelState.PreviewIndex)
                CALL @Station.DropItemDraw.Entry
                ; чтение и удаление ключа описания модели
                LD DE, (@ModelDescriptionState.ItemIndex)
                CALL @Station.DropItemDraw.Entry
                ; чтение и удаление ключа панели 28
                LD DE, (@DrawItemState.Index28)
                CALL @Station.DropItemDraw.Entry
                ; чтение последнего ключа панели 29 перед хвостовым DropItemDraw
                LD DE, (@DrawItemState.Index29)
                JP @Station.DropItemDraw.Entry

                endmodule
                endmodule
