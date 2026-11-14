                module Intro
                module InitializeIntro
                ; Физические данные [два экранных ресурса](../../Docs/IntroScreenResources.md)
                ; Документация [вступление и передача загрузчику](../../Docs/IntroStationTransition.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
; -----------------------------------------
; Перенос завершающего загрузчика, вывод экрана и создание таблиц вступления
; исходная запись 3, файловые смещения #0200..#02B2
                ; In:
                ;   загружены исходные 44 сектора по 6400..8FFF из файлового смещения 0100, экран и рабочие банки доступны
                ;   7FFD разблокирован, IM=1, I=3F, выбран проверенный ROM 48K, период IRQ в модели 69888
                ;   KSTATE по 5C00 и 5C04 равны FF, ROM-сканер модели получает отпущенные клавиши, проверка Space задаётся отдельно
                ;   в сквозных профилях FRAMES=0, входной IFF=0, код, временный стек 5FFF и рабочие области не перекрываются посторонними данными
                ; Out:
                ;   код загрузчика перенесён в 5D3B, распаковщик с потоком перенесён в 6E31, подготовлены эффекты и финальная прокрутка
                ;   после 300 шагов либо выхода по точному значению BE строки Space управление передаётся в 5D3B
                ;   SP=5FFF после штатного счётчика, SP=5FF9 при досрочном выходе из RunTimedEffect
                ;   BC=7FFE, AF=BE6A при выходе по Space в проверенных профилях N=0, 1 и 2, это не выход штатного счётчика N=300
                ;   AF' сохранён с ненулевым контрольным значением A55A, IX=0 на границе загрузчика
                ;   IY=5C0F, I=3F, IM=1 на границе загрузчика, его собственные команды ещё не исполнены
                ;   в четырёх профилях с N=0, 1, 2 и 300 кадрами FRAMES=45+3*N, IFF=1 для N=0 и 300, IFF=0 для N=1 и 2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IX, IY, SP, IFF, R, FRAMES, экран, рабочие банки, цепочки, стек и 7FFD
                ; Note:
                ;   четыре сценария исполнили весь участок на исходных байтах с настоящим ROM, включая 300 кадров последнего эффекта
                ;   InitializeLookupEffect получает IY=5C29, BuildMirroredTexture, InitializeColumnEffect и InitializeScrolledTexture получают 5C0F
                ;   при N больше нуля DrawFinalTextureFrame и DrawScrolledTexture получают IY=5C0F, это проверено без подготовки внутренних входов
                ;   договоры самостоятельных процедур с IY=5C3A не переносятся на эти контексты без оговорок, системный перенос описан отдельно
                ;   Space опрашивается моделью отдельно от отпущенных клавиш ROM, иные KSTATE, начальный FRAMES, время и нативный запуск не доказаны
                ;   переносимый загрузчик самостоятельно сбрасывает SP и готовит обращение к TR-DOS, дальнейшее чтение не входит в договор этой границы
; -----------------------------------------
Entry:          DI
                LD HL, #65B7
                LD DE, @IntroStationRuntime.Entry
                LD BC, #0100
                LDIR
                LD SP, #5FFF
                SUB A
                OUT (#FE), A
                LD HL, #6E31
                LD DE, #4000
                LD BC, #1B00
                LDIR
                LD HL, #8931
                LD DE, #6E31
                LD BC, #1B00
                LDIR
                LD C, #FF
                CALL @Intro.FillBitmap.Entry
                LD IY, #5C3A
                LD (@IntroStackSnapshot.Value.Stack), SP
                CALL @Intro.SelectIntroPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #3FFF
                LD (HL), L
                LDIR
                LD HL, #6000
                LD DE, #6001
                LD BC, #03FF
                LD (HL), L
                LDIR
                ; -----------------------------------------
                ; очистка исходного окна от #8F93 до #BFFF после переноса распаковщика
                ; первый ноль распространяется вперёд, копия по #7493 и далее остаётся в банке 5
                LD HL, @IntroScreenConst.SourceClearFrom
                LD DE, @IntroScreenConst.SourceClearFrom + 1
                LD BC, @IntroScreenConst.SourceClearRest
                LD (HL), #00
                LDIR
                ; -----------------------------------------
                LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #12FF
                LD (HL), L
                LDIR
                LD A, #16
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #3FFF
                LD (HL), L
                LDIR
                CALL @Intro.BuildScreenTables.Entry
                CALL @Intro.BuildIntroTexture.Entry
                CALL @Intro.BuildAlternatingTexture.Entry
                EI
                CALL @Intro.InitializeLookupEffect.Entry
                CALL @Intro.BuildMirroredTexture.Entry
                CALL @Intro.InitializeColumnEffect.Entry
                CALL @Intro.InitializeScrolledTexture.Entry
                LD C, #00
                CALL @Intro.FillBitmap.Entry
                LD HL, #5800
                LD DE, #5801
                LD BC, #01FF
                LD (HL), #88
                LDIR
                LD BC, #012C
                LD HL, #661E
                CALL @Intro.RunTimedEffect.Entry
EnterStation:   JP @IntroStationRuntime.Entry


                endmodule
                endmodule
