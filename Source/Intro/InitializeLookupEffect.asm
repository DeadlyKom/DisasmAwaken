                module Intro
                module InitializeLookupEffect
                ; Физические параметры [источники и потребители](../../Docs/IntroPhysicalParameters.md)
                ; Документация [столбцовый и табличный эффекты](../../Docs/IntroGeneratedEffects.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
; -----------------------------------------
; Создание трёх развёрнутых обработчиков, фазовых таблиц и таблицы указателей эффекта
; исходная запись 3, файловые смещения #099C..#0A69
                ; In:
                ;   банк 4 содержит #1300 байтов, доступны страница #64, три записи фаз, банк 1 и общий буфер
                ;   7FFD разблокирован, стек и ПЗУ удовлетворяют профилю PresentAttributes
                ; Out:
                ;   созданы цепочки #9100, #9900 и #A800, таблицы фаз и 4096 байтов указателей банка 1
                ;   после 40 обновлений фаз подготовлены писатель и атрибуты, выход через PresentAttributes
                ;   выбран банк 1, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IX, IYL, R, IFF, операнды, текстура, таблицы, 7FFD и стек
                ; Note:
                ;   восемь проходов проверили три цепочки, таблицы и вывод с исходным ПЗУ
                ;   проверены исходный операнд #6D40 и обе раскладки, нативный запуск не подтверждён
; -----------------------------------------
Entry:          LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #AD00
                LD BC, #1300
                LDIR
                CALL @Intro.SelectIntroPage.Entry
                LD DE, #9100
                LD HL, #6D78
                LD BC, #4006
                CALL @Intro.RepeatPattern.Entry
                DEC HL
                LD DE, #6BED
                CALL @Intro.WriteJump.Entry
                LD DE, #9900
                LD HL, #6D7E
                LD BC, #000F
                CALL @Intro.RepeatPattern.Entry
                DEC HL
                DEC HL
                LD (HL), #C9
                LD HL, #A800
                LD DE, #C000
                LD C, #26
WriterRow:      LD B, #08
WriterWord:     LD (HL), #E1
                INC HL
                LD (HL), #22
                INC HL
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                INC E
                INC E
                DJNZ @Intro.InitializeLookupEffect.WriterWord

                LD E, #00
                INC D
                DEC C
                JR NZ, @Intro.InitializeLookupEffect.WriterRow                  ; переход, если ещё не созданы писатели всех 38 строк


                LD DE, #6BBC
                CALL @Intro.WriteJump.Entry
                LD HL, #9800
                ; создание таблицы старших полубайтов для индексов от 0 до 255
BuildNibble:    LD A, L
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                LD (HL), A
                INC L
                JR NZ, @Intro.InitializeLookupEffect.BuildNibble                ; переход, если таблица ещё не содержит все 256 старших полубайтов


                LD H, #64
                LD DE, #9400
                LD C, #09
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #06
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #08
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #05
                CALL @Intro.BuildPhaseTable.Entry
                LD HL, #F000
                LD D, #B0
                LD C, #00
                ; создание очередных 16 указателей на страницы результата, начало диапазона задаёт D
PointerRow:     LD E, D
                LD B, #10
CheckUpper:     LD A, E
                CP #80
                JR C, @Intro.InitializeLookupEffect.CheckLower                  ; переход, если значение меньше верхнего ограничения #80


                LD A, #7F
CheckLower:     CP #70
                JR NC, @Intro.InitializeLookupEffect.StorePage                  ; переход, если значение не меньше нижнего ограничения #70


                LD A, #70
                ; расчёт страницы результата после ограничения значения диапазоном #70..#7F
StorePage:      SUB #70
                SRL A
                ADD A, #89
                LD (HL), A
                DEC E
                INC HL
                DJNZ @Intro.InitializeLookupEffect.CheckUpper

                ; изменение операнда LD A,n на #00 либо #80 для уменьшения D через итерацию
                LD A, #80
                ADD A, #80
                LD (#6D40), A
                JR NZ, @Intro.InitializeLookupEffect.CountPtrRow                ; переход, если новая фаза равна #80 и D уменьшать не нужно


                DEC D
CountPtrRow:    DEC C
                JR NZ, @Intro.InitializeLookupEffect.PointerRow                 ; переход, если ещё не созданы все 256 строк указателей


                LD IXL, #28
WarmPhases:     CALL @Intro.AdvanceTexturePhases.Entry
                DEC IXL
                JR NZ, @Intro.InitializeLookupEffect.WarmPhases                 ; переход, если ещё не выполнены 40 начальных обновлений фаз


                LD A, #88
                LD (@IntroAttributeNibbleSeeds.A0), A
                LD IXL, #89
                LD DE, #8000
                LD BC, #0040
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
