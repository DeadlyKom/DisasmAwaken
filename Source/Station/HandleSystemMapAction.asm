                module Station
                module HandleSystemMapAction
                ; Документация [реальные курсоры сцены, точный нулевой выход, координатные переносы и периодическая цель](../../Docs/SystemMapAction.md)
                ; -----------------------------------------
                ; Выбор ближайшего варианта системы либо закрытие карты с отключением её периодического обновления
                ; исходная запись 4, файловые смещения #1AE7..#1B2F
                ; In:
                ;   HL запасной рисователь карты, DE индекс элемента 20, BC контекст, AF полный селектор, IX выбранная FInterfaceItem
                ;   действуют договоры RepaintAndFlag и CloseMenuOnRow, банк станции 0 выбран, исходный список и хвосты сдвига доступны
                ;   для селектора 1 MapSelection содержит выбранный пятибайтовый ключ, KARTA загружена в банк 1, переключение страниц разрешено
                ;   VariantPanelState.ItemIndex задаёт читаемые X и Y панели, Cursor0..Cursor5 банка 1 соответствуют текущим точкам сцены
                ;   действуют договоры DescribeKeyBanked, SelectNearestMapVariant, BeginScreenUpdate, условных панелей и EndScreenUpdate, HALT корректно пробуждается
                ; Out:
                ;   при Carry общего обработчика сразу возвращён его результат, последующие ветви выбора и закрытия не исполняются
                ;   для селектора не 1 после разрешённого общего пути выполнен CloseMenuOnRow, при его Z=1 HL=EmptyCallback и PeriodicCall заменён на этот адрес
                ;   при Z=0 CloseMenuOnRow его результаты возвращены без самостоятельной записи PeriodicCall
                ;   для селектора 1 количество N=max(((XOR четырёх выбранных байтов) AND 7)-1,0), при N=0 немедленно возвращён результат DescribeKeyBanked
                ;   нулевой путь возвращает HL и DE характеристики ключа, BC сохранён от входа DescribeKeyBanked, AF=0044 либо 0042, AF' содержит страницу возврата и её OR-флаги
                ;   при N=1..6 MapSelection.Variant содержит индекс первого ближайшего из N текущих курсоров, Origin собран из физических X и Y панели
                ;   после выбора последовательно вызваны BeginScreenUpdate, TryDrawSystemInfo и TryDrawVariantPanel, затем EndScreenUpdate
                ;   после экранного цикла HL, DE, BC и альтернативные общие пары соответствуют выполненным панелям, A=10 и F сохранён от последнего рисователя либо его проверки
                ;   при экранном цикле CurrentPage=10, указатель возобновлён, UpdateBlocked=0, PeriodicCall определяется последним DrawVariantPanel при его присутствии
                ;   IY, I, IFF и IM сохранены при договоре IRQ, IX может измениться подготовкой ресурсов панели, SP обычного возврата входному+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX по подготовке ресурсов, MapSelection.Variant, Minimum, рабочий ключ, список, callback, экраны и текстовое состояние
                ; Note:
                ;   нулевая ветвь сама не меняет номер варианта и периодическую цель, предшествующие эффекты RepaintAndFlag этим не отменяются
                ;   Origin является целым упакованным словом, Target=PointerWord-(8×((Origin+0404) AND FFFF)+0603) по модулю 65536, переносы между X и Y не разделяются
                ;   при равных квадратах расстояний прежний индекс остаётся, принудительной замены последним совпадением нет
                ;   отключение PeriodicCall относится к Z результата CloseMenuOnRow, оно не выполняется просто от любого неселективного A
                ;   собственный переход SelectVariant по 784F обходит общий префикс, номер вариантов и ресурсы обязаны быть подготовлены вызывающим окружением
                ;   модель использует настоящие ресурсные координаты после DrawVariantPanel, независимый oracle всего повторного bitmap не заявлен
                ; -----------------------------------------
                ; обновление общей геометрии и порядка карты перед разбором селектора
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если общий обработчик вернул Carry, выбор и закрытие не разрешены

                ; проверка селектора 1 для выбора варианта
                DEC A
                JP Z, @Station.HandleSystemMapAction.SelectVariant              ; переход, если селектор равен 1, вычислить ближайший вариант

                ; удаление карты только при совпадении символьных строк указателя и начала окна
                CALL @Station.CloseMenuOnRow.Entry
                JR NZ, @Station.HandleSystemMapAction.CloseResult               ; переход, если символьные строки различаются, периодическую цель самостоятельно не менять

                ; обновление периодической цели пустым RET после разрешённого закрытия
                LD HL, @Station.EmptyCallback.Entry
                LD (@MenuCommandState.PeriodicCall), HL
CloseResult:    RET

                ; чтение полного выбранного ключа для количества вариантов и его характеристики
SelectVariant:  LD A, (@MapSelection.Variant)
                LD HL, (@MapSelection.FirstWord)
                LD DE, (@MapSelection.SecondWord)
                CALL @Station.DescribeKeyBanked.Entry
                RET Z                                                           ; выход, если количество вариантов равно нулю, ближайший вариант не вычислять

                ; сохранение ненулевого количества в AF на время чтения координат панели через альтернативный набор
                EX AF, AF'
                ; поиск физических FInterfaceItem.X и Y текущей панели вариантов
                LD HL, (@VariantPanelState.ItemIndex)
                XOR A
                CALL @Station.GetItemField.Entry
                ; создание упакованного Origin, младший X и старший Y, это не пиксельное начало текстового окна
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                ; выбор банка KARTA с сохранением экранного бита
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; восстановление количества и поиск первого ближайшего из текущих курсоров
                EX AF, AF'
                CALL @Map.SelectNearestMapVariant.Entry
                ; возврат банка станции после записи нового MapSelection.Variant
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; создание теневого снимка перед последовательным обновлением двух зависимых панелей
                CALL @Station.BeginScreenUpdate.Entry
                ; обновление информации о выбранной системе только при точном присутствии её рисователя
                CALL @Station.TryDrawSystemInfo.Entry
                ; обновление карты и её ресурсов только при точном присутствии рисователя
                CALL @Station.TryDrawVariantPanel.Entry
                ; показ обновлённого базового экрана и возобновление указателя
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
