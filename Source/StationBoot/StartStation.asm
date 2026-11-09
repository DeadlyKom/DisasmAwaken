                module StationBoot
                module StartStation
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
                ; Документация [физические ключи и размеры фонов](../../Docs/StationBootResourceTables.md)
; Документация [StationBoot](../../Docs/FunctionDetails/StationBoot.md)
; -----------------------------------------
; Загрузка банков карты, музыки, справки, 3D и языка, выбор фона, настройка устройств и запуск цикла станции
; исходная запись 4, файловые смещения #0389..#05CD
; In:
;   ядро станции перенесено в #6322, загрузчик находится по исходному адресу #4000, TR-DOS доступен
; Out:
;   подключён банк 0, установлен IM 2, разрешены прерывания, управление передано #9A59
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, побочные эффекты загруженных модулей и TR-DOS
; Note:
;   банки 1, 3, 7, 4 и 6 получают карту, музыку, справку, D3D и язык соответственно
;   из stscr выбирается один из 16 фонов по младшему полубайту R, чтение учитывает исходные физические сектора
;   каждый обработчик рисования из таблицы #F0FD получает индекс элемента в операнд своей обёртки
;   проверяются порты #1F, #FBDF и #FFDF с учётом сохранённых настроек, назначение остальных полей требует отдельного разбора
; -----------------------------------------
Entry:          LD A, #09
                LD (#5D06), A
                LD A, #11
                CALL @Station.SelectMemoryPage.Entry
                ; Выбор файла карты для банка 1.
                LD HL, @StationBootFileKeys.Karta.Name
                LD DE, #5CDD
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
                LD DE, #5CDD
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
                LD DE, #5CDD
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
                LD DE, #5CDD
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
                LD HL, @StationBootFileKeys.Lang.Name
                LD DE, #5CDD
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
                LD DE, #5CDD
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
                LD HL, #3838
                LD (#DAFE), HL
                LD (#DAFC), HL
                LD (#DAFB), HL
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
                LD (#9CA6), HL
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
                LD A, (#99B0)
                RES 7, A
                CPL
                AND E
                LD (#6639), A
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
                LD A, (#99AE)
                RES 7, A
                CPL
                AND E
                LD (#65A8), A
                XOR A
                LD (#9CAA), A
                LD BC, @SettingsText.Interface
                LD DE, @InterfaceChoices.MouseOption
                CALL @Station.FormatSettingsLabel.Entry
                LD BC, @SettingsText.Controls
                LD DE, @ControlOptions.Unknown00
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


PrepareWorld:   LD HL, (#6DA9)
                LD A, #0A
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
                LD (#6304), HL
                LD A, #11
                CALL @Station.SelectMemoryPage.Entry
                LD DE, (#983F)
                LD HL, (#9841)
                CALL @Map.CenterMapView.Entry
                LD A, #10
                CALL @Station.SelectMemoryPage.Entry
                LD A, (#99B3)
                LD (#9B62), A
                LD HL, #993D
                LD (#6309), HL
                IM 2
                EI
                JP @Station.MainLoop.Entry


                endmodule
                endmodule
