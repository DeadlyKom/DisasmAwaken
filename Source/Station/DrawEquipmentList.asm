                module Station
                module DrawEquipmentList
                ; Документация [параллельные таблицы, счётчик маркера 80, физические кадры и особый EXX-выход](../../Docs/EquipmentListPanels.md)
                ; -----------------------------------------
                ; Рамка оснащения, заголовки колонок и сохранение счётчика попыток вывода
                ; исходная запись 4, файловые смещения #14D3..#14F7
                ; In:
                ;   активный LD HL содержит EquipmentListState.ItemIndex, штатно 38, либо первый байт заменён на C9
                ;   при активном коде действуют договоры DrawCaptionItem, SetupEquipmentColumns и PrintEquipmentRows, текущий ключ доступен
                ;   ScriptSelection.EquipmentBase задаёт полное слово TopRow, банк станции 0 выбран, KARTA загружена, paging разрешён, HALT получает корректный IRQ
                ; Out:
                ;   при активном коде рамка и заголовок зарегистрированы, EquipmentRow=FF, колонки настроены и KeySize получен из текущего ключа
                ;   после заголовков Carry пропускает тело, тогда RowCount=0, AF=0044, альтернативный AF содержит статус заголовка
                ;   иначе AF содержит счётчик попыток и его INC-флаги, AF' последний статус PrintEquipmentRows, RowCount равен A
                ;   HL, DE, BC и альтернативные общие пары соответствуют выполненному телу, включая особый ранний выход внутри EXX
                ;   IX, IY, I, IFF и IM сохранены при договоре IRQ, SP обычного возврата входному+2, страницы 10 и 18 сохраняют экранный бит
                ;   при временном C9 весь контекст и память сохранены, даже индекс и строки не читаются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', окно, bitmap, курсор, RowCount, EquipmentRow, рабочий ключ и текстовые операнды
                ; Note:
                ;   RenderRows по 7244 принимает HL от прокрутки и обходит рамку, сброс EquipmentRow, настройку колонок, заголовки и чтение TopRow
                ;   RenderRows всё равно исполняет PrintEquipmentRows, EX AF и сохранение RowCount, его счётчик также включает попытку маркера
                ;   независимый oracle проверяет всё тело, bitmap рамки проверяется договором DrawCaptionItem, полного нативного запуска нет
                ; -----------------------------------------
                ; чтение изменяемого индекса панели для рамки и заголовка
Entry:          LD HL, #0000
                CALL @Station.DrawCaptionItem.Entry
                ; обновление наведения, новая рамка больше не содержит прежнюю XOR-полосу
                LD A, #FF
                LD (@ScriptSelection.EquipmentRow), A
                ; подготовка четырёх колонок и характеристики текущей модели станции
                CALL @Station.SetupEquipmentColumns.Entry
                ; печать исходных заголовков Кол, Цена, Вес и Уст
                LD HL, @EquipmentListText.Headings
                CALL @Station.PrintText.Entry
                ; обнуление счётчика на пути отказа заголовков с сохранением их Carry
                EX AF, AF'
                XOR A
                EX AF, AF'
                JP C, @Station.DrawEquipmentList.SaveRowCount                   ; переход, если заголовки вернули Carry, сохранить нулевое число строк без тела

                ; чтение полного слова прокрутки, сценарные читатели используют только его младший байт
                LD HL, (@ScriptSelection.EquipmentBase)
                ; RenderRows принимает HL прокрутки без повторной рамки и заголовков
RenderRows:     CALL @Station.PrintEquipmentRows.Entry
                ; обмен итогового статуса и счётчика попыток, запись ограничителя наведения
SaveRowCount:   EX AF, AF'
                LD (@EquipmentListState.RowCount), A
                RET

                endmodule
                endmodule
