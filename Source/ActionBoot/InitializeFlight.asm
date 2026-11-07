                module ActionBoot
                module InitializeFlight
                ; Имена ресурсов [физические ключи](../../Docs/ActionBootFileKeys.md)
                ; Документация [загрузка банков и вход в полёт](../../Docs/ActionFlightCycle.md)
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
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, R, банки, таблицы, потоковое состояние и системные поля TR-DOS
                ; Note:
                ;   при входе из RelocateBootstrap сохранённый HL равен #623D
                ;   дочерние вызовы каталога и загрузки используют успешные ответы, обработка ошибок диска этой моделью не подтверждена
                ;   в модели оригинальные данные диска подставлены на входе TR-DOS, вызовы и переходы Z80 исполняются
; -----------------------------------------
Entry:          LD SP, #C000
                PUSH HL
                LD DE, #6000
                LD BC, #1F8F
                LDIR
                LD A, #1E
                CALL @Action.SelectMemoryPage.Entry
                LD A, #09
                LD (#5D06), A
                LD HL, @ActionBootFileKeys.Panel
                LD DE, #5CDD
                LD BC, #0009
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
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, @ActionBootFileKeys.Voxal
                LD DE, #5CDD
                LD BC, #0009
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
                LD (#5E20), HL
                LD (#5E23), A
                CALL @ActionBoot.LoadFileToBank.Entry
                LD HL, @ActionBootFileKeys.Control
                CALL @ActionBoot.GetFileLocation.Entry
                LD HL, #DADE
                CALL @ActionBoot.LoadFileAtAddress.Entry
                LD A, #1C
                CALL @Action.SelectMemoryPage.Entry
                LD HL, @ActionBootFileKeys.Object3D
                LD DE, #5CDD
                LD BC, #0009
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
