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
                ;   загружены 44 сектора по #6400..#8FFF из файлового смещения #0100, экран и рабочие банки доступны
                ;   выбранное ПЗУ содержит обработчик IM 1, 7FFD разблокирован, доступны периодические IRQ
                ; Out:
                ;   код загрузчика перенесён в #5D3B, распаковщик перенесён в #6E31, подготовлены эффекты
                ;   после 300 шагов либо выхода по Space управление передаётся в #5D3B
                ;   SP=#5FFF после штатного счётчика, SP=#5FF9 при досрочном выходе из RunTimedEffect
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, IFF, R, экран, рабочие банки, цепочки и стек
                ; Note:
                ;   четыре сценария исполнили весь участок с исходным ПЗУ, включая все 300 кадров
                ;   переносимый загрузчик самостоятельно сбрасывает SP и готовит обращение к TR-DOS
; -----------------------------------------
Entry:          DI
                LD HL, #65B7
                LD DE, #5D3B
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
                LD (#65B4), SP
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
                LD HL, #8F93
                LD DE, #8F94
                LD BC, #306C
                LD (HL), #00
                LDIR
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
EnterStation:   JP #5D3B


                endmodule
                endmodule
