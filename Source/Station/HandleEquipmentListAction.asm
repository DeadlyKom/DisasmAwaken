                module Station
                module HandleEquipmentListAction
                ; Документация [первый выбор, повторная сделка, кодировка количества и физическая прокрутка](../../Docs/EquipmentTrade.md)
                ; -----------------------------------------
                ; Выбор описания либо подтверждение сделки оснащения, закрытие группы и прокрутка списка
                ; исходная запись 4, файловые смещения #1421..#14BB
                ; In:
                ;   HL запасной рисователь списка оснащения, DE индекс элемента, BC контекст, AF полный селектор, IX текущая FInterfaceItem
                ;   действуют договоры RepaintAndFlag, CloseMenuOnRow и удаления по изменяемым индексам, банк станции 0 выбран
                ;   EquipmentBase полное слово прокрутки, EquipmentRow байт наведения либо FF, байтовая сумма их младших частей задаёт доступное описание
                ;   для повторной сделки LANG находится в банке 6, доступны состояние игрока и таблицы оснащения
                ;   действуют договоры выбранных рисователей, экранного цикла и ScrollWindowRows с callback DrawEquipmentList.RenderRows
                ;   для прокрутки окно и хвосты списка допустимы, ввод освобождается, HALT получает сохраняющий контекст IRQ
                ; Out:
                ;   при Carry RepaintAndFlag возвращён его результат без выполнения остальных ветвей
                ;   для селектора 1 и EquipmentRow=FF возврат без собственных записей после общего префикса, A=0,F=50 OR Carry до INC
                ;   для селектора 1 индекс=(EquipmentBase.low+EquipmentRow) AND FF, старший байт базы при выборе игнорируется
                ;   новый индекс записан в EquipmentInfoState.TextIndex, TopRow описания обнулён полным словом
                ;   при новом индексе исполнены BeginScreenUpdate, TryDrawEquipmentInfo, TryDrawEquipmentList и EndScreenUpdate, LANG не вызывается
                ;   при прежнем индексе EventCode=5 для нулевого OwnedMode, иначе 6, исполнен исходный LANG и возвращён банк станции
                ;   после LANG всегда исполнены BeginScreenUpdate, DrawItem00, DrawEquipmentList и EndScreenUpdate, включая отказ сделки
                ;   рисователь списка сбрасывает EquipmentRow в FF и обновляет счётчик строк по своему договору
                ;   при селекторе не 1 совпадение строки CloseMenuOnRow удаляет текущий список, затем Index37, Index36 и EquipmentInfoState.ItemIndex
                ;   иначе настроены колонки, снята прежняя полоса, EquipmentRow=FF, RenderCall=RenderRows и EndLimit=29
                ;   ScrollWindowRows получает A=24 и полное прежнее EquipmentBase, полный возвращённый HL записан в EquipmentBase
                ;   HL, DE, BC, AF и альтернативные пары соответствуют исполненному экранному, текстовому, закрывающему либо прокручивающему помощнику
                ;   IX по общему префиксу и LANG, IY, I, IFF и IM сохранены при договорах помощников и IRQ, SP после RET входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX по LANG, состояние игрока по событию, текст, список, экран и операнды помощников
                ; Note:
                ;   первое подтверждение другой строки меняет только описание, сделка требует повторения того же байтового индекса
                ;   общий префикс сдвигает 128 физических байтов даже для последнего рисователя, ранний FF этих эффектов не отменяет
                ;   ненулевой OwnedMode не является набором независимых флагов, он целиком выбирает продажу
                ;   низкое окно может вернуть индекс без шага, снимок атрибутов и страница 10 всё равно следуют договору ScrollWindowRows
                ;   собственной записи PeriodicCall при закрытии нет, поведение отличается от группы моделей корабля
                ;   bitmap тела принятой прокрутки сверен независимо, весь bitmap рамок и нативный запуск здесь не проверены
                ; -----------------------------------------
                ; обновление общей геометрии и порядка списка до разбора селектора
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если общий обработчик вернул Carry, не выбирать строку и не закрывать панели

                ; проверка селектора 1 для выбора строки либо подтверждения сделки
                DEC A
                JP Z, @Station.HandleEquipmentListAction.SelectRow              ; переход, если селектор равен 1, проверить строку оснащения

                ; проверка закрытия по совпадению символьных строк указателя и начала окна
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.HandleEquipmentListAction.PrepareScroll         ; переход, если строки различаются, подготовить прокрутку вместо закрытия

                ; чтение индекса панели покупки для удаления
                LD DE, (@DrawItemState.Index37)
                ; удаление панели покупки после закрытия текущего списка
                CALL @Station.DropItemDraw.Entry
                ; чтение индекса панели продажи
                LD DE, (@DrawItemState.Index36)
                ; удаление панели продажи
                CALL @Station.DropItemDraw.Entry
                ; чтение индекса документации оснащения
                LD DE, (@EquipmentInfoState.ItemIndex)
                ; удаление документации без собственной замены периодической цели
                CALL @Station.DropItemDraw.Entry
                RET

                ; подготовка колонок и числового предела станции для callback прокрутки
PrepareScroll:  CALL @Station.SetupEquipmentColumns.Entry
                ; чтение отступа и текущего числа строк прежней полосы
                LD DE, (@EquipmentListState.HoverArea)
                LD A, (@ScriptSelection.EquipmentRow)
                ; удаление прежней XOR-полосы только при выбранной строке
                CALL @Station.XorRowIfSelected.Entry
                ; обновление выбранной строки в FF перед изменением тела списка
                LD A, #FF
                LD (@ScriptSelection.EquipmentRow), A
                ; выбор внутреннего рисователя строк без повторной рамки
                LD HL, @Station.DrawEquipmentList.RenderRows
                ; обновление CALL прокрутки адресом RenderRows
                LD (@ScrollState.RenderCall), HL
                ; выбор предельного начального индекса 29 для исходных тридцати строк
                LD HL, #001D
                ; обновление границы прокрутки
                LD (@ScrollState.EndLimit), HL
                ; выбор отступа 24 пикселя и полного прежнего индекса
                LD A, #18
                LD HL, #0000
                CALL @Station.ScrollWindowRows.Entry
                ; сохранение полного возвращённого индекса без отбрасывания старшего байта
                LD (@ScriptSelection.EquipmentBase), HL
                RET

                ; чтение строки для выбора описания либо повторной сделки
SelectRow:      LD A, (@ScriptSelection.EquipmentRow)
                ; проверка отсутствия строки по переполнению FF в ноль
                INC A
                RET Z                                                           ; выход, если строка равна FF, собственный выбор не выполнять

                ; восстановление исходного номера после проверочного INC
                DEC A
                LD L, A
                ; чтение младшего байта базы для байтового индекса описания
                LD A, (@ScriptSelection.EquipmentBase)
                ; расчёт индекса по модулю 256, старший байт базы не участвует
                ADD A, L
                LD L, A
                ; чтение прежнего индекса для отделения первого выбора от сделки
                LD A, (@EquipmentInfoState.TextIndex)
                ; проверка совпадения описания с выбранным индексом
                CP L
                JR Z, @Station.HandleEquipmentListAction.ConfirmTrade           ; переход, если индекс уже выбран, выполнить торговое событие

                LD A, L
                ; обновление индекса описания после первого выбора другой строки
                LD (@EquipmentInfoState.TextIndex), A
                ; обновление полного TopRow описания нулём
                LD HL, #0000
                LD (@EquipmentInfoState.TopRow), HL
                ; создание снимка перед обновлением зависимых панелей
                CALL @Station.BeginScreenUpdate.Entry
                ; обновление документации только при точном присутствии её рисователя
                CALL @Station.TryDrawEquipmentInfo.Entry
                ; обновление списка только при точном присутствии его рисователя
                CALL @Station.TryDrawEquipmentList.Entry
                ; показ описания и списка с возобновлением указателя
                CALL @Station.EndScreenUpdate.Entry
                RET

                ; чтение изменяемого полного режима оснащения
ConfirmTrade:   LD A, #00
                ; проверка нулевого режима покупки
                OR A
                LD A, #05
                JR Z, @Station.HandleEquipmentListAction.RunEvent               ; переход, если OwnedMode равен нулю, оставить событие покупки 5

                ; расчёт события продажи 6 для любого ненулевого режима
                INC A
                ; обновление события перед входом в LANG
RunEvent:       LD (@ScriptCallState.EventCode), A
                ; выбор банка LANG для исходного сценария
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                ; выполнение исходных условий сделки оснащения
                CALL @Text.RunMarketScript.Entry
                ; возврат банка станции после нормального завершения LANG
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; создание снимка перед обновлением статуса и списка после любого исхода сделки
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem00.Entry
                ; обновление списка с удалением прежнего наведения
                CALL @Station.DrawEquipmentList.Entry
                ; показ результата с возобновлением указателя
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
