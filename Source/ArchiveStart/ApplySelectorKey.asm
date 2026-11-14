                module ArchiveStart
                module ApplySelectorKey
                ; Документация [клавиши и селекторы](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; фиксация нового нажатия, обновление старого слоя и подключение нового маршрута
                ; In:
                ;   IX - запись FArchiveStartKey для первой нажатой клавиши группы
                ; Out:
                ;   повтор того же кода оставляет фиксацию и селекторы без изменений
                ;   новый код сохраняется даже на границе, в этом случае селектор не меняется
                ;   при допустимом шаге перерисованы слои старого выбора, затем подключён маршрут нового
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, отображение страницы
                ; Note:
                ;   Limit задаёт границу конкретного шага, верхнюю для увеличения и нулевую для уменьшения
                ;   младшие селекторы принимают значения 0..3, старшие 0..2
                ;   обработчики Redraw и Commit возвращаются с сохранённым стеком вызова
                ; -----------------------------------------
                ; проверка, совпадает ли код клавиши с последним зафиксированным нажатием стороны
Entry:          LD E, (IX + @FArchiveStartKey.Latch)
                LD D, (IX + @FArchiveStartKey.Latch + 1)
                LD A, (DE)
                CP (IX + @FArchiveStartKey.LatchCode)
                RET Z                                                           ; выход, если нажатие этой клавиши уже зафиксировано

                ; фиксация нового нажатия и проверка границы селектора для выбранного шага
                LD A, (IX + @FArchiveStartKey.LatchCode)
                LD (DE), A
                LD E, (IX + @FArchiveStartKey.Selector)
                LD D, (IX + @FArchiveStartKey.Selector + 1)
                LD A, (DE)
                CP (IX + @FArchiveStartKey.Limit)
                RET Z                                                           ; выход, если селектор достиг границы для выбранного шага

                ; запись стороны для построителя маски и подключение страницы меню
                LD A, (IX + @FArchiveStartKey.Side)
                LD (@ArchiveStartSelector.Side), A
                LD A, (@ArchiveStartData.Page.DefaultCode)
                CALL @ArchiveStart.SelectPage.Dispatch

                ; вызов построителя со старым значением селектора, возврат через явный адрес
                PUSH DE
                PUSH IX
                LD E, (IX + @FArchiveStartKey.Redraw)
                LD D, (IX + @FArchiveStartKey.Redraw + 1)
                EX DE, HL
                LD DE, @ArchiveStart.ApplySelectorKey.StoreSelection
                PUSH DE
                JP (HL)

                ; обновление значения селектора на знаковый шаг из записи
StoreSelection: POP IX
                POP DE
                LD A, (DE)
                LD C, A
                LD A, (IX + @FArchiveStartKey.Step)
                ADD A, C
                LD (DE), A

                ; подключение полосы по новому значению, обработчик вернётся к сканеру группы
                LD E, (IX + @FArchiveStartKey.Commit)
                LD D, (IX + @FArchiveStartKey.Commit + 1)
                EX DE, HL
                JP (HL)

                endmodule
                endmodule
