                module StationBoot
                module StartStation
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
                ; Документация [физические ключи и размеры фонов](../../Docs/StationBootResourceTables.md)
                ; Полный контекст запуска [разбор](../../Docs/StationBootstrap.md#передача-в-основной-цикл-станции)
; Документация [StationBoot](../../Docs/FunctionDetails/StationBoot.md)
; -----------------------------------------
; Загрузка банков карты, музыки, справки, 3D и языка, выбор фона, настройка устройств и запуск цикла станции
; исходная запись 4, файловые смещения #0389..#05CD
                ; In:
                ;   ядро STATIONF перенесено в #6322, исполняется исходная фиксированная копия загрузчика #4000..#42B4
                ;   оригинальные ключи файлов, таблица шестнадцати длин stscr, список FInterfaceItem и сохранённые настройки доступны
                ;   TR-DOS обеспечивает успешные обычные возвраты, загружает запрошенные выделенные сектора и сохраняет исполняемую копию и стек
                ;   7FFD разблокирован, рабочие банки доступны, действуют договоры Music.Initialize, UnpackResource и станционных помощников
                ;   CPU-стек отделён от кода, источников и целей модулей, вмещает рамки всех вызываемых процедур
                ;   до завершения IM2-таблицы IRQ не вмешиваются, конечный договор дан на границе JP в MainLoop
                ; Out:
                ;   PC=#9A59, SP равен входному SP, I=#80, IM=2, IFF=1, аппаратная страница и CurrentPage равны #10
                ;   HL=#993D, DE упакованные младшие байты OriginLow, BC=#FF00 OR ((0-floor(Height/2)) AND #FF)
                ;   AF - A полный KeyMask настройки InterfaceChoices.MusicMode, F сохранён от последнего ADC при центрировании Y карты
                ;   HL'=2758, DE' последнее сохранённое слово HR фона, BC'=00xx с последним младшим счётчиком вывода HR
                ;   AF' сохраняет выход последнего DOS, распаковка и последующая настройка его не меняют
                ;   IX указывает маркер интерфейса после привязки, для исходного списка IX=#F3DD, обработаны 46 записей
                ;   IY сохраняет выход последнего DOS, распаковка и последующая настройка его не меняют, в модели IY=#5C3A
                ;   карта находится в банке 1, музыка и распакованный фон в банке 3, справка в 7, D3D в 4, LANG в 6
                ;   последние пять атрибутов фона банка 3 по #DAFB..#DAFF заменены #38, байт #DAFC записан дважды
                ;   IM2-таблица #8000..#8100 заполнена #81, по #8181 находится JP #9AEA, таблицы строк созданы по #8200/#8300, столбцов по #8400
                ;   DrawListState.HeadOperand=#F3DE, MenuCommandState.Hidden=0, SecondaryPointState.Cursor=#993D
                ;   X/Y/Width/Height всех предшествующих маркеру записей восстановлены из сохранённых полей, операнды рисователей получают их индексы
                ;   MapViewState получает размеры из SavedWidth/SavedHeight панели карты и начало из текущего ключа, StationIrqState.ModeOperand получает A
                ;   PointerInputState.JoyDisabled и MousePollState.Disabled определены исходными портовыми пробами и сохранёнными настройками
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по TR-DOS, I, IM, IFF, R и PC хвостовым переходом
                ;   банки загруженных файлов, распакованный фон и его пять атрибутов, состояние и аппаратные регистры AY инициализации музыки
                ;   IM2-таблица и переход, три экранные таблицы, геометрия интерфейса, индексы рисователей, подписи настроек, начало и размеры карты
                ;   операнды мыши, джойстика и музыкального IRQ, список перерисовки, системные поля DOS, временные рамки CPU-стека и 7FFD
                ; Note:
                ;   функция 0E с A=03 читает полные выделенные сектора, каталожная длина не отбрасывает их хвосты
                ;   фон выбирается из 16 по младшей тетраде прочитанного R, фон и музыка занимают непересекающиеся части банка 3
                ;   IN A,(1F) фактически обращается к #021F, следующие пробы обращаются к #FBDF и #FFDF
                ;   JoyDisabled равен признаку ненулевого J AND 1F, объединённому с инверсией младших семи битов JoyOption через AND
                ;   MousePollState.Disabled равен совместному признаку MX=FF и MY=FF, объединённому с инверсией MouseOption через AND
                ;   настройка геометрии уменьшает отдельно SavedWidth на два и SavedHeight на три, затем умножает упакованное слово на восемь modulo 65536
                ;   в исходной таблице это даёт область 152 на 96, центрирование сохраняет исходное отсечение по Sign обёрнутой суммы
                ;   ближайшие к DOS границы отдельно проверены настоящим ROM 5.04T, новый сквозной контекст использует подставленный дисковый интерфейс
                ;   16 новых профилей проверили все фоны, восемь бинарных сочетаний проб портов, регистры кроме R/T, таблицы, четыре загруженных модуля и их хвосты
                ;   полная независимая RAM-модель, все сохранённые настройки, дисковые ошибки, аппаратные IRQ и нативная игра этой проверкой не доказаны
; -----------------------------------------
                ; Поиск сравнивает восемь символов имени и отдельный байт типа файла.
Entry:          LD A, @FTrDosFileKey
                LD (@TrDosState.SearchKeyLength), A
                LD A, #11
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор файла карты для банка 1.
                LD HL, @StationBootFileKeys.Karta.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #13
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор музыкального файла и последующая инициализация проигрывателя.
                LD HL, @StationBootFileKeys.Muz1.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #DB00
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                CALL @Music.Initialize.Entry
                LD A, #17
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор файла справки для банка 7.
                LD HL, @StationBootFileKeys.Help.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #DB00
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #14
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор модуля просмотра моделей для банка 4.
                LD HL, @StationBootFileKeys.D3D.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                XOR A
                LD L, A
                LD H, A
                LD (#C200), HL
                LD (#C202), A
                LD (#C20E), HL
                LD (#C212), HL
                LD (#C218), HL
                LD (#C21A), HL
                LD (#C210), HL
                LD (#C216), HL
                LD HL, #7FFF
                LD (#C20C), HL
                LD (#C214), HL
                LD (#C21C), HL
                LD A, #16
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор модуля LANG для банка 6.
                ; Документация [секторный хвост LANG](../../Docs/AllocatedSectorSuffixes.md#повторы-внутри-файлов)
                LD HL, @StationBootFileKeys.Lang.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #13
                CALL @Station.SelectMemoryPage.Entry
                ; Поиск каталожной записи исходного файла фонов.
                LD HL, @StationBootFileKeys.StationScreens.Name
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD C, #0A
                CALL @TrDos.Dispatch
                LD A, C
                LD C, #08
                CALL @TrDos.Dispatch
                ; Выбор одного из шестнадцати фонов по младшей тетраде R.
                LD A, R
                AND #0F
                LD C, A
                LD L, A
                LD H, #00
                LD DE, @StationBackdropSizes.Backdrop00.Sectors
                ADD HL, DE
                PUSH HL
                INC C
                EX DE, HL
                XOR A
SumLengths:     DEC C
                JR Z, @StationBoot.StartStation.LocateScreen                    ; переход, если все предыдущие длины просуммированы, вычислить позицию экрана


                ADD A, (HL)
                INC HL
                JR @StationBoot.StartStation.SumLengths


                ; Расчёт физического трека и сектора с добавлением начала файла.
LocateScreen:   LD DE, (#5CEB)
                LD C, A
                AND #0F
                ADD A, E
                LD E, A
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                ADD A, D
                LD D, A
                LD A, C
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                ADD A, D
                LD D, A
                LD A, E
                AND #0F
                LD E, A
                ; Чтение указанного числа секторов и распаковка фона на месте.
                POP HL
                LD B, (HL)
                LD HL, #C000
                LD C, #05
                CALL @TrDos.Dispatch
                LD HL, #C000
                LD DE, #C000
                CALL @Station.UnpackResource.Entry
                ; -----------------------------------------
                ; Замена последних пяти атрибутов распакованного фона
                LD HL, #3838
                LD (#DAFE), HL
                LD (#DAFC), HL
                LD (#DAFB), HL
                ; Байты DAFB..DAFF получают 38, перекрывающиеся слова повторно записывают DAFC.
                ; -----------------------------------------
                LD A, #10
                CALL @Station.SelectMemoryPage.Entry
                DI
                LD HL, #8000
                LD A, H
                LD I, A
                LD DE, #8001
                LD BC, #0100
                LD (HL), #81
                LDIR
                LD HL, #8181
                LD (HL), #C3
                INC L
                LD (HL), #EA
                INC L
                LD (HL), #9A
                LD HL, #F3DE
                LD (@DrawListState.HeadOperand), HL
                LD HL, #8200
                LD DE, #4000
StoreLineAddr:  LD (HL), D
                INC H
                LD (HL), E
                DEC H
                INC D
                LD A, D
                AND #07
                JP NZ, @StationBoot.StartStation.CountLineAddr                  ; переход, если следующая строка не первая в знакоместе, адрес готов


                LD A, E
                ADD A, #20
                LD E, A
                JR C, @StationBoot.StartStation.CountLineAddr                   ; переход, если сложение E с #20 дало перенос, следующая треть уже выбрана


                LD A, D
                SUB #08
                LD D, A
CountLineAddr:  INC L
                JR NZ, @StationBoot.StartStation.StoreLineAddr                  ; переход, если не записаны все 256 индексов строк, продолжить таблицу


                INC H
                INC H
                XOR A
ColumnGroup:    LD B, #08
RepeatColumn:   LD (HL), A
                INC L
                DJNZ @StationBoot.StartStation.RepeatColumn

                INC A
                CP #20
                JR C, @StationBoot.StartStation.ColumnGroup                     ; переход, если записаны не все 32 группы столбцов, начать следующую


                LD HL, #0000
                LD (#6307), HL
                LD A, #BF
                LD (#66CF), A
                LD A, #FF
                LD (#66D1), A
                LD A, #08
                LD (#6501), A
                LD A, #02
                LD (#66CD), A
                LD HL, #0000
                LD (#6550), HL
                LD HL, #6000
                LD (#64B3), HL
                IN A, (#1F)
                AND #1F
                LD A, #01
                JR NZ, @StationBoot.StartStation.ApplyJoystick                  ; переход, если младшие пять битов порта #1F ненулевые, оставить признак опроса равным одному


                DEC A
ApplyJoystick:  LD E, A
                LD A, (@InterfaceChoices.JoyOption + FSettingWord.ValueOrRow)
                RES 7, A
                CPL
                AND E
                LD (@PointerInputState.JoyDisabled), A
                LD BC, #FBDF
                IN A, (C)
                INC A
                LD E, #01
                JR Z, @StationBoot.StartStation.ProbeMouseIdle                  ; переход, если порт #FBDF вернул #FF, сохранить первый признак равным одному


                DEC E
ProbeMouseIdle: LD B, #FF
                IN A, (C)
                INC A
                LD A, #01
                JR Z, @StationBoot.StartStation.CombineMouse                    ; переход, если порт #FFDF вернул #FF, сохранить второй признак равным одному


                DEC A
CombineMouse:   AND E
                LD E, A
                LD A, (@InterfaceChoices.MouseOption + FSettingWord.ValueOrRow)
                RES 7, A
                CPL
                AND E
                LD (@MousePollState.Disabled), A
                XOR A
                LD (@MenuCommandState.Hidden), A
                LD BC, @SettingsText.Interface
                LD DE, @InterfaceChoices.MouseOption
                CALL @Station.FormatSettingsLabel.Entry
                LD BC, @SettingsText.Controls
                LD DE, @ControlOptions.MouseOption
                CALL @Station.FormatSettingsLabel.Entry
                CALL @Station.RestoreAllBounds.Entry
                LD IX, #F0FD
                LD C, #00
                LD DE, #0010
BindItemIndex:  LD A, (IX + @FInterfaceItem.X)
                CP #80
                JR Z, @StationBoot.StartStation.PrepareWorld                    ; переход, если встретился маркер #80 списка элементов, закончить привязку индексов


                LD L, (IX + @FInterfaceItem.DrawHandler)
                LD H, (IX + @FInterfaceItem.DrawHandler + 1)
                INC HL
                LD (HL), C
                INC HL
                LD (HL), #00
                INC C
                ADD IX, DE
                JP @StationBoot.StartStation.BindItemIndex


PrepareWorld:   LD HL, (@MapPanelState.ItemIndex)
                LD A, @FInterfaceItem.SavedWidth
                CALL @Station.GetItemField.Entry
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                DEC L
                DEC H
                DEC L
                DEC H
                DEC H
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD (@MapViewState.Width), HL
                LD A, #11
                CALL @Station.SelectMemoryPage.Entry
                LD DE, (#983F)
                LD HL, (#9841)
                CALL @Map.CenterMapView.Entry
                LD A, #10
                CALL @Station.SelectMemoryPage.Entry
                LD A, (@InterfaceChoices.MusicMode + FSettingWord.KeyMask)
                LD (@StationIrqState.ModeOperand), A
                LD HL, #993D
                LD (@SecondaryPointState.Cursor), HL
                IM 2
                EI
                JP @Station.MainLoop.Entry


                endmodule
                endmodule
