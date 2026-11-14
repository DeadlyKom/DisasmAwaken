                module Intro
                module BuildMirroredTexture
                ; Документация [отражение и размещение текстуры](../../Docs/IntroMirroredTexture.md)
                ; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)
                ; -----------------------------------------
                ; Построение отражённой текстуры и перенос результата в страницу 4
                ; исходная запись 3, файловые смещения #0AB6..#0B30
                ; In:
                ;   банк 1 содержит строки указателей, доступны таблицы и цепочки InitializeLookupEffect
                ;   доступны источник страницы #64 и назначение в банке 4, порт 7FFD разблокирован
                ;   стек и ПЗУ удовлетворяют условиям кадрового IRQ, прерывания не вмешиваются во временные стеки
                ; Out:
                ;   из центрального блока 32 на 32 буфера 64 на 38 строится симметричная текстура 64 на 64, #1000 байтов в банке 4 и общем буфере
                ;   HL=#9000, DE=#D000, BC=#7FFD, A=#11, IXL=0, IY и IXH сохраняются
                ;   выбрана страница #11, IRQ разрешены, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IXL, R, IFF, фазовые операнды, цепочки, текстура, стек и 7FFD
                ; Note:
                ;   выбираются колонки 16..47 и строки 3..34 исходного буфера, результат вычитания #89 по модулю 256 отражается по обеим осям
                ;   дополнительная модель в 1281 сценарии проверила каждую выбранную точку, четыре симметричных выхода и все значения байта без IRQ
                ;   замена CALL по #6BDA на JP возвращает управление из второй выборки без общего вывода кадра
                ;   12 сквозных сценариев с настоящим рендером и ПЗУ, дополнительно 32 проверки отражения
                ;   произвольные времена IRQ и нативный запуск не проверены
                ; -----------------------------------------
Entry:          EI
                ; Превращение второго вызова выборщика в хвостовой переход без экранного переноса.
                LD A, #C3
                LD (@Intro.PresentLookupTexture.SecondSampler), A
                LD A, #50
                CALL @Intro.SelectTexturePointerRow.Entry
                SUB A
                LD (@IntroState.LookupHL), A
                LD (@IntroState.LookupBCAlt), A
                LD (@IntroState.LookupHLAlt), A
                LD (@IntroState.LookupDEAlt), A
                LD H, #64
                LD DE, #9400
                LD C, #03
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #05
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.RenderLookupTexture.Entry
                EI
                ; Выбор центральных 32 колонок и 32 строк, адрес #80D0 соответствует строке 3 и колонке 16.
                LD HL, #80D0
                LD DE, #8000
                LD IXL, #20
MirrorRow:      LD BC, #0020
                PUSH BC
                LDIR
                POP BC
                ADD HL, BC
                PUSH HL
                LD H, D
                LD L, E
                DEC L
                LD B, #20
                ; Расчёт байтового кода по модулю 256, заём при вычитании #89 переносится между полубайтами.
MirrorPixel:    LD A, (HL)
                SUB #89
                LD (HL), A
                LD (DE), A
                INC DE
                DEC L
                DJNZ @Intro.BuildMirroredTexture.MirrorPixel

                POP HL
                DEC IXL
                JR NZ, @Intro.BuildMirroredTexture.MirrorRow                    ; переход, если ещё не обработаны все 32 строки отражаемой текстуры


                ; Отражение первых 2048 байтов в обратном порядке во вторую половину.
                LD HL, #87FF
                LD DE, #8800
                LD BC, #0800
MirrorHalf:     LD A, (HL)
                LD (DE), A
                DEC HL
                INC DE
                DEC BC
                LD A, B
                OR C
                JR NZ, @Intro.BuildMirroredTexture.MirrorHalf                   ; переход, если ещё не отражены все #0800 байтов второй половины


                LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #8000
                LD DE, #C000
                LD BC, #1000
                LDIR
                JP @Intro.SelectIntroPage.Entry


                endmodule
                endmodule
