                module Station
                module DrawSecondaryList
                ; Документация [второй список, общая печать, выбор и события LANG](../../Docs/SecondaryEquipmentRows.md)
                ; -----------------------------------------
                ; Рамка, заголовки и счётчик строк второго списка оснащения
                ; исходная запись 4, перенос STATIONF с 05CE в 6322, адреса 73DE..7402
                ; In:
                ;   банк станции 0 выбран, начальный индекс элемента в операнде LD HL равен нулю
                ;   текст, рамка, ключ и таблицы подготовлены согласно DrawCaptionItem, SetupEquipmentColumns и PrintSecondaryRows
                ;   RenderRows принимает HL полный индекс, рамка и колонки уже подготовлены
                ; Out:
                ;   на прямом входе отрисована рамка, колонки настроены, Row=FF и напечатаны общие заголовки
                ;   при Carry заголовков тело пропущено, RowCount=0, AF=0044, AF' содержит статус заголовков
                ;   иначе регистры по PrintSecondaryRows, AF содержит счётчик попыток, AF' последний статус, RowCount=A
                ;   RenderRows меняет счётчик и тело, но сам не обновляет Row, SP обычного возврата увеличен на два
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', экран, курсор, ключ и рабочие операнды детей
                ; Note:
                ;   оба входа приходят в общий SaveRowCount, попытка маркера 80 включена в счётчик
                ;   модель прямого входа использует действительный IM2 при HALT рамки, вызывающий путь не установлен
                ; -----------------------------------------
                ; рисование рамки элемента и настройка числовых колонок
Entry:          LD HL, #0000
                CALL @Station.DrawCaptionItem.Entry
                CALL @Station.SetupEquipmentColumns.Entry
                ; обновление выбранной строки после рисования рамки
                LD A, #FF
                LD (@SecondaryEquipmentState.Row), A
                ; вывод общих заголовков и проверка результата печати
                LD HL, @EquipmentListText.Headings
                CALL @Station.PrintText.Entry
                EX AF, AF'
                XOR A
                EX AF, AF'
                JP C, @Station.DrawSecondaryList.SaveRowCount                   ; переход, если печать заголовков вернула Carry, сохранить нулевой счётчик

                ; чтение начального индекса второго списка
                LD HL, (@SecondaryEquipmentState.TopRow)
                ; рисование строк с подготовленными параметрами окна
RenderRows:     CALL @Station.PrintSecondaryRows.Entry
                ; обновление числа строк из альтернативного счётчика печатателя
SaveRowCount:   EX AF, AF'
                LD (@SecondaryEquipmentState.RowCount), A
                RET

                endmodule
                endmodule
