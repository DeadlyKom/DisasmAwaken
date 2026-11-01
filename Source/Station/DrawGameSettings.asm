                module Station
                module DrawGameSettings
                ; Документация [два CR-списка, общий хвост значений, полный индекс и счётчик обработанных полей](../../Docs/SettingsRowPanels.md)
                ; -----------------------------------------
                ; Рамка установок игры, сброс подсветки и сохранение числа обработанных значений
                ; исходная запись 4, файловые смещения #18E3..#18FB
                ; In:
                ;   GameSettingsPanelState.ItemIndex содержит индекс FInterfaceItem, штатно 42, либо Entry временно содержит C9
                ;   геометрия, шрифт, таблицы, стек и IRQ удовлетворяют DrawCaptionItem, TopRow и значения подготовлены
                ;   для обычного Entry выполняются договоры SetupGameSettingsText и PrintGameSettingsRows
                ; Out:
                ;   после рамки PanelHoverState.GameSettingsRow=FF, окно и колонка значений настроены, TopRow передан печатателю
                ;   HL, DE и BC принадлежат печатателю, основной AF содержит его альтернативный счётчик и флаги
                ;   AF' содержит основной результат печатателя, HL', DE', BC', IX и IY сохранены
                ;   GameSettingsPanelState.RowCount получает полный байт обработанных значений, включая последний отказ, TopRow не меняется
                ;   страница не переключается собственным кодом, I, IFF и IM сохраняются при договоре IRQ, SP после RET входному+2
                ;   RenderRows принимает HL от прокрутки, пропускает рамку, сброс подсветки, настройку и чтение TopRow, затем выполняет печать и запись RowCount
                ;   при временном C9 в Entry сохраняются регистры, флаги и память, SP после RET входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', окно, курсор, bitmap, номер подсветки, RowCount и изменяемые операнды помощников
                ; Note:
                ;   RowCount задаёт D обработчика наведения, число начатых значений не является числом успешно нарисованных строк
                ;   пробуждение HALT рамки требуется только для Entry, внутренний RenderRows нового HALT не выполняет
                ; -----------------------------------------
                ; чтение изменяемого индекса панели установок игры
Entry:          LD HL, #0000
                ; рисование рамки и заголовка с подготовкой окна
                CALL @Station.DrawCaptionItem.Entry
                ; сброс прежней XOR-полосы после замены фона
                LD A, #FF
                LD (@PanelHoverState.GameSettingsRow), A
                ; отключение переноса и выбор колонки игровых значений
                CALL @Station.SetupGameSettingsText.Entry
                ; чтение полного слова прокрутки установок игры
                LD HL, (@GameSettingsPanelState.TopRow)
                ; RenderRows принимает HL от прокрутки без новой рамки
RenderRows:     CALL @Station.PrintGameSettingsRows.Entry
                ; получение альтернативного счётчика обработанных значений
                EX AF, AF'
                ; обновление байтового ограничения наведения по обработанным значениям
                LD (@GameSettingsPanelState.RowCount), A
                RET

                endmodule
                endmodule
