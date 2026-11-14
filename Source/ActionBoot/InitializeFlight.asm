                module ActionBoot
                module InitializeFlight
                ; Имена ресурсов [физические ключи](../../Docs/ActionBootFileKeys.md)
                ; Документация [загрузка банков и вход в полёт](../../Docs/ActionFlightCycle.md)
                ; Режимы CPU [граница перед DI](../../Docs/ActionFlightCycle.md#режимы-cpu-на-границе-startflight)
                ; Документация [адреса старых операндов CONTROL](../../Docs/ControlsLegacyLoadChain.md)
                ; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
                ; -----------------------------------------
                ; Перенос ядра в #6000, загрузка графических банков и запуск полётного режима
                ; исходная запись 17, файловые смещения #0043..#00ED
                ; In:
                ;   HL указывает исходное полётное ядро, доступны файлы оригинального диска и запись в 7FFD
                ;   код загрузчика уже перенесён в #4200, IRQ не вмешиваются в загрузку
                ; Out:
                ;   ядро перенесено в #6000, загружены банки 6, 3, 1 и 4, панель распакована
                ;   построены таблицы #9100..#97FF, инициализированы потоки и текстовое окно
                ;   выбрана страница #19, SP=#BFFE хранит исходный HL, управление передано StartFlight через JP
                ;   на границе перед первой DI StartFlight I, IM и IFF сохраняют результат последнего TR-DOS, свой начальный режим подготовитель не восстанавливает
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, I, IM, IFF по TR-DOS, R, банки, таблицы, потоковое состояние и системные поля TR-DOS
                ; Note:
                ;   TrDosState.SearchKeyLength получает размер FTrDosFileKey, поиск включает восемь символов имени и тип, это числовая длина
                ;   при входе из RelocateBootstrap сохранённый HL равен #623D
                ;   дочерние вызовы каталога и загрузки используют успешные ответы, обработка ошибок диска этой моделью не подтверждена
                ;   в модели оригинальные данные диска подставлены на входе TR-DOS, вызовы и переходы Z80 исполняются
                ;   отдельная модель ROM проверяет полные сектора, CONTROL перекрывает 34 байта суффикса CONTROL0 по #DADE
                ;   [секторные хвосты](../../Docs/AllocatedSectorSuffixes.md#повторы-внутри-файлов)
                ;   при запуске через вступление записи по #5E20, #5E21 и #5E23 меняют хвост его копии, код CONTROL остаётся в банке 1
                ;   в модели TR-DOS 5.04T следующие чтения секторов в #5D25 перезаписывают эти три байта общей RAM
                ;   [проверка окна #5DA0..#5EDA](../../Docs/ControlsTemporaryModule.md)
                ;   18 условных профилей сохраняют явно заданные I/IM/IFF дисковой службы до A82D, следующая DI сбрасывает только IFF
                ;   в этих профилях интерфейс DOS подставлен и аппаратные IRQ подавлены, все заданные режимы не объявляются выходами настоящей ROM
                ; -----------------------------------------
Entry:          LD SP, #C000
                PUSH HL
                LD DE, #6000
                LD BC, #1F8F
                LDIR
                LD A, #1E
                CALL @Action.SelectMemoryPage.Entry
                ; Поиск сравнивает восемь символов имени и отдельный байт типа файла.
                LD A, @FTrDosFileKey
                LD (@TrDosState.SearchKeyLength), A
                LD HL, @ActionBootFileKeys.Panel
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #C000
                PUSH HL
                LD A, #03
                LD C, #0E
                CALL @TrDos.Dispatch
                POP HL
                LD D, H
                LD E, L
                CALL @Action.UnpackResource.Entry
                LD A, #1B
                CALL @Action.SelectMemoryPage.Entry
                LD HL, @ActionBootFileKeys.Voxal0
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, @ActionBootFileKeys.Voxal
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD HL, #EC00
                PUSH HL
                LD A, #03
                LD C, #0E
                CALL @TrDos.Dispatch
                POP HL
                LD A, #19
                CALL @Action.SelectMemoryPage.Entry
                LD HL, @ActionBootFileKeys.Control0
                CALL @ActionBoot.GetFileLocation.Entry
                ; Запись координат и числа секторов CONTROL0 по адресам операндов старой копии.
                LD (@Controls.LoadLegacyPackedBlock.Entry + 1), HL
                LD (@Controls.LoadLegacyPackedBlock.SectorCount + 1), A
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, @ActionBootFileKeys.Control
                CALL @ActionBoot.GetFileLocation.Entry
                ; Выбор начала CONTROL в банке 1 как адреса загрузки, вызов временного модуля здесь не выполняется.
                LD HL, @Controls.RunTemporaryModule.Entry
                CALL @ActionBoot.LoadFileAtAddress.Entry
                LD A, #1C
                CALL @Action.SelectMemoryPage.Entry
                LD HL, @ActionBootFileKeys.Object3D
                LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                CALL @ActionBoot.LoadFileToBank.Entry
                LD A, #18
                CALL @Action.SelectMemoryPage.Entry
                CALL @ActionBoot.InitializeRandomStates.Entry
                CALL @ActionBoot.BuildExponentialTable.Entry
                CALL @ActionBoot.BuildLogarithmTable.Entry
                CALL @ActionBoot.BuildBitmapTables.Entry
                LD A, #19
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.InitializeTextWindow.Entry
                JP @Action.StartFlight.Entry


                endmodule
                endmodule
