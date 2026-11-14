                module Intro
                module InitializeColumnEffect
                ; Физические параметры [источники и потребители](../../Docs/IntroPhysicalParameters.md)
                ; Документация [столбцовый и табличный эффекты](../../Docs/IntroGeneratedEffects.md)
                ; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
                ; -----------------------------------------
                ; Создание обработчика #D000, таблиц выбора столбцов и суммированной текстуры для эффекта
                ; исходная запись 3, файловые смещения #07C1..#0859
                ; In:
                ;   банк 4 содержит #1000 байтов исходной текстуры, банки 1 и 2 доступны для записи
                ;   7FFD разблокирован, IM=1, IY=#5C3A, проверенный 48K ROM, клавиши отпущены и KSTATE по 5C00 и 5C04 равны FF
                ;   14 байтов ниже SP доступны, стек не пересекает код, таблицы указателей, матрицы и рабочую текстуру 8000..BFFF
                ;   IFF разрешён для HALT, проверен период 69888, следующий IRQ не вмешивается во временный SP писателя
                ; Out:
                ;   в банке 1 созданы цепочка #D000, 16 таблиц столбцов и 32 табличных хвоста
                ;   банк 2 содержит 64 страницы суммы квадратов 2 на 2 с добавкой #40
                ;   HL содержит последнее слово выбранной матрицы, DE=#6100, BC=#699B, AF от фазы
                ;   HL'=#6929, DE'=#C8C8, BC'=0, AF' сохранён, IX=0, IYL получает младшую тетраду #69A2
                ;   страница #11, SP после RET равен входному SP+2
                ;   при исходном 69A2=FF на HALT приходит IY=5C0F, перенос младшего слова FRAMES увеличивает 5C4F вместо 5C7A
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IX, IYL, R, таблицы, текстура, стек, 7FFD и состояние IRQ
                ;   системный байт 5C4F при исходном 69A2=FF и переполнении младшего слова FRAMES
                ; Note:
                ;   рабочая копия первой строки по C000 даёт неизменённого соседа последней строки, ядро читает только C000..C040
                ;   профиль IRQ отличается от самостоятельного договора PresentAttributes, IYL изменён до вызова
                ;   восемь дополнительных профилей исполнили IRQ с IY=5C0F, счётчик FRAMES для переноса задан перед HALT
                ;   восемь сценариев проверили исходный генератор, все таблицы и вывод с настоящим ROM
                ;   нативный запуск и произвольные состояния IRQ не проверены
                ; -----------------------------------------
Entry:          CALL @Intro.SelectIntroPage.Entry
                LD DE, #D000
                LD HL, #6B5A
                LD BC, #4019
                CALL @Intro.RepeatPattern.Entry
                LD (HL), #C9
                LD IXH, #D8
                LD HL, #D800
                LD DE, #0100
                LD C, #10
ColumnTable:    PUSH HL
                LD IXL, #40
                LD B, #60
                ; проверка допустимости старшего байта адреса столбца в диапазоне #D8..#E7
CheckUpper:     LD A, H
                CP #E8
                JR C, @Intro.InitializeColumnEffect.CheckLower                  ; переход, если старший байт адреса меньше #E8


                SUB A
CheckLower:     CP #D8
                JR NC, @Intro.InitializeColumnEffect.StoreColumn                ; переход, если старший байт адреса не меньше #D8


                SUB A
StoreColumn:    LD (IX + #00), A
                INC IXL
                ADD HL, DE
                DJNZ @Intro.InitializeColumnEffect.CheckUpper

                INC IXH
                LD HL, #FFFB
                ADD HL, DE
                EX DE, HL
                POP HL
                DEC C
                JR NZ, @Intro.InitializeColumnEffect.ColumnTable                ; переход, если ещё не созданы все 16 таблиц выбора столбцов


                LD D, #DA
                LD A, #20
CopyTail:       LD E, #E0
                LD HL, @IntroColumnTailSamples.P00
                LD BC, #0020
                LDIR
                DEC A
                JR NZ, @Intro.InitializeColumnEffect.CopyTail                   ; переход, если ещё не заполнены хвосты всех 32 страниц


                LD (#67FE), A
                LD IXL, #00
                CALL @Intro.ExpandTextureRows.Entry
                LD HL, #8000
                PUSH HL
                LD DE, #C000
                LD BC, #0100
                LDIR
                POP HL
TextureRow:     LD L, #00
                ; расчёт суммы соседнего квадрата 2 на 2 плюс #40 по модулю 256
SumSquare:      LD A, (HL)
                INC H
                ADD A, (HL)
                INC L
                ADD A, (HL)
                DEC H
                ADD A, (HL)
                DEC L
                ADD A, #40
                LD (HL), A
                INC L
                BIT 6, L
                JR Z, @Intro.InitializeColumnEffect.SumSquare                   ; переход, если ещё не рассчитаны 64 байта строки


                LD E, L
                LD D, H
                LD BC, #00C0
                LD L, B
                LDIR
                INC H
                BIT 6, H
                JR Z, @Intro.InitializeColumnEffect.TextureRow                  ; переход, если ещё не преобразованы все 64 страницы текстуры


                SUB A
                LD (@IntroAttributeNibbleSeeds.A0), A
                LD IXL, #C0
                LD DE, #D800
                LD BC, #0100
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
