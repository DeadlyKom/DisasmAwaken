                module Station
                module DrawModelListPanel
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [полный путь рамки, характеристики, выбора полей и D3D, сохранённый счётчик строк](../../Docs/ModelListPanel.md)
                ; -----------------------------------------
                ; Рисование списка рыночных либо текущих кораблей и скимеров с обновлением высоты наведения
                ; исходная запись 4, файловые смещения #0A8C..#0AE2
                ; In:
                ;   ModelListState.ItemIndex содержит актуальный индекс FInterfaceItem, первоначально загрузчик записывает 25, Opcode равен 21 для работы либо C9 для отключения
                ;   при активном входе выполнены договоры DrawCaptionItem, DescribeCurrentKey для рынка и DrawPreviewPrices для выбранных текстов
                ;   ShipPanelState.Selector и OwnedMode задают таблицу и режим, текущие индексы при собственном просмотре находятся в соответствующих допустимых диапазонах
                ;   порт и CurrentPage согласованы, исходно банк станции 0, paging не заблокирован, стек вне сменяемого окна
                ;   HALT рамки получает пробуждение с сохранением существенного контекста по договору DrawBandSync
                ; Out:
                ;   HL - позиция завершения ценового тела, DE - смещение 2*(уровень-1) на рынке либо адрес временной границы собственной записи
                ;   BC - сохранён на рынке, при собственном режиме B сохранён, C равен текущему индексу выбранной модели
                ;   AF - количество строк и F после вычисления счётчика из CursorY по договору DrawPreviewPrices, тот же A записан в ModelListState.HoverRows
                ;   HL', DE', BC' сохранены, AF' - A'=(исходная CurrentPage AND F8) OR 10 и F' от логического OR этой страницы
                ;   IX, IY, I и IFF сохраняются при договоре пробуждения, итоговые порт и CurrentPage выбирают банк 0 с ROM 1
                ;   рамка и заголовок элемента нарисованы, Style=0, Column2X=36, PanelHoverState.ShipsRow=FF, состояние цен D3D и курсор соответствуют реальному выводу
                ;   отключённый C9 сохраняет все регистры, флаги и память без чтения индекса, SP обычного возврата в обоих случаях равен входному SP+2
                ; Corrupt:
                ;   при активном входе HL, DE, BC, AF, AF' и графическое состояние вызываемых помощников
                ; Note:
                ;   на рынке DescribeCurrentKey даёт уровень 1..16, выбирается одна из шестнадцати реальных FModelAvailability, при OwnedMode ненулевом этот вызов отсутствует
                ;   станция выбирает ShipBase и текущий ShipIndex при Selector=0, любой ненулевой Selector выбирает SkimmerBase и SkimmerIndex
                ;   D3D выбирает скимерный текст только при Selector=1, поэтому произвольные другие ненулевые значения не нормализуются и имеют разные соглашения на двух слоях
                ;   банк 1 посещается только для характеристики рынка, банк 4 всегда для цен, старшие управляющие разряды страницы сохраняются с принудительным ROM 1
                ;   HoverRows является старшим байтом непосредственного LD DE обработчика UpdateShipListHover, исходное 30 после рисунка заменяется вычисленным счётчиком
                ;   отказ печати не обязательно даёт ноль строк, счётчик вычисляется из курсора, панель не проверяет статус текста перед его сохранением
                ; -----------------------------------------
                ; чтение изменяемого индекса панели, C9 отключает весь вход
Entry:          LD HL, #0000
                ; реальные регистрация, рамка и заголовок по общему договору элемента
                CALL @Station.DrawCaptionItem.Entry
                ; задание обычной политики текста и отмена прежней полосы наведения
                XOR A
                LD (@TextWindow.Style), A
                LD A, #FF
                LD (@PanelHoverState.ShipsRow), A
                ; задание колонки цены на 36 пикселях
                LD A, @PreviewPriceConst.PriceColumn
                LD (@TextStreamState.Column2X), A
                ; проверка режима, ноль требует рыночную базу по уровню текущей системы
                LD A, (@ShipPanelState.OwnedMode)
                OR A
                JR Z, @Station.DrawModelListPanel.MarketBase                    ; переход, если OwnedMode равен нулю, получить рыночную базу из характеристики системы

                ; проверка селектора текущего корабля либо скимера
                LD A, (@ShipPanelState.Selector)
                OR A
                LD A, (@CurrentModels.ShipIndex)
                JR Z, @Station.DrawModelListPanel.HaveIndex                     ; переход, если Selector равен нулю, оставить текущий индекс корабля

                ; выбор текущего индекса скимера для любого ненулевого селектора станции
                LD A, (@CurrentModels.SkimmerIndex)
HaveIndex:      JR @Station.DrawModelListPanel.PriceCall

                ; получение настоящей банковой характеристики текущего пятибайтового ключа
MarketBase:     CALL @Station.DescribeCurrentKey.Entry
                ; расчёт смещения двухбайтовой FModelAvailability по уровню 1..16
                DEC L
                LD A, L
                ADD A, A
                LD E, A
                LD D, #00
                ; выбор начала физического массива уровней и рассчитанной записи
                LD HL, @ModelAvailability.Level01
                ADD HL, DE
                ; проверка поля таблицы, ноль выбирает ShipBase, неноль SkimmerBase
                LD A, (@ShipPanelState.Selector)
                OR A
                JR Z, @Station.DrawModelListPanel.ReadBase                      ; переход, если Selector равен нулю, читать поле ShipBase

                ; выбор соседнего физического поля SkimmerBase
                INC HL
ReadBase:       LD A, (HL)
                ; передача выбранной базы в альтернативный A для ценового рисователя
PriceCall:      EX AF, AF'
                ; выбор банка 4 с исходным D3D для реального ценового текста
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                ; передача режима в H и полного селектора в A без нормализации
                LD A, (@ShipPanelState.OwnedMode)
                LD H, A
                LD A, (@ShipPanelState.Selector)
                ; вызов настоящего рисователя цен и его временных разделителей
                CALL @D3D.DrawPreviewPrices.Entry
                ; возврат в станционный банк 0 с сохранением альтернативного счётчика
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; получение счётчика из альтернативного AF и сохранение его в операнде наведения
                EX AF, AF'
                LD (@ModelListState.HoverRows), A
                RET

                endmodule
                endmodule
