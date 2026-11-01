                module Music
                module RenderChannelB
                ; Документация [синтез трёх каналов](../../Docs/MusicSynthesis.md)
                ; -----------------------------------------
                ; Синтез сэмпла, орнамента, тона, шума и огибающей канала B
                ; исходная запись 10, файловые смещения #05ED..#06CC
                ; In:
                ;   L' содержит восьмибитовую сумму вкладов предыдущих каналов, H', DE' и BC' сохраняются
                ;   IXH и IXL содержат текущие шум и микшер, SP может указывать на данные предшествующего синтеза
                ;   состояние канала равно 00 либо FF, переключатель ограничения скольжения равен 00 либо 1D
                ;   доступны исходные заголовки сэмпла и орнамента, читаемые шаги, таблица громкости DC00 и слова периода DD00
                ;   прерывания запрещены, банк MUZ1 доступен для записи, I, IM и IY не задают дополнительных параметров
                ; Out:
                ;   собственного RET нет, выбран один из входов следующего FinishChannelB
                ;   при FF A=0 и F=50 OR входной Carry, выбран UpdateGate без восстановления AF, ресурсы канала не читаются
                ;   при 00 AF' содержит рассчитанный уровень, его F соответствует OR уровня либо SRL ShiftControl при FixedLevelBit=1
                ;   обновлены позиции сэмпла и орнамента, вычислен и записан текущий тон, амплитуда пока остаётся в альтернативном AF
                ;   сохранение накопителей шума, огибающей и тона определяется разрядами LevelModes
                ;   при шаге скольжения обновлено смещение, при достижении цели текущая нота заменена целевой, младший байт смещения обнулён
                ;   A передаёт уменьшенный либо нулевой счётчик в StoreSlideDelay, либо выбран вход перезагрузки или RestoreLevel
                ;   при разрешённом синтезе BC равно прежнему SlideOffset этого канала, SP указывает за прочитанным словом периода
                ;   IY, I, IM и IFF сохранены, указатели и исходные ресурсы сэмпла и орнамента не изменены
                ;   L' увеличен на вклад огибающей по модулю 256, H', DE' и BC' сохранены
                ;   при пропуске синтеза SP, BC и альтернативный AF сохранены, биты микшера канала добавляются через OR IXL
                ;   IXH заменён вкладом канала только при его шумовом режиме
                ; Corrupt:
                ;   HL, DE, BC, AF, HL' только L', AF', IX, временный SP, SampleCursor, OrnamentCursor, AmplitudeAdjust, накопители и поля скольжения по условиям, R
                ; Note:
                ;   заголовок FMusicLoopHeader содержит LoopPosition и Length, шаг FMusicSampleStep содержит два управляющих байта и слово тона
                ;   A и B теряют перенос второго удвоения позиции сэмпла, C умножает полное слово на четыре
                ;   сумма ноты и орнамента оборачивается в байте, значения от 128 выбирают индекс 0, индексы 96..127 читают соседние данные
                ;   достижение цели сохраняет старший байт разности в SlideOffset, а не принудительно обнуляет всё слово
                ;   счётчики и амплитуда окончательно записываются следующим FinishChannelB, настоящий SP восстанавливает OutputAyFrame
                ;   независимая модель проверяет все пары управляющих байтов и промежуточные границы каждого канала, IRQ и нативный звук отдельно не подтверждены
                ; -----------------------------------------
                ; проверка числового состояния разрешения синтеза B
Entry:          LD A, #FF
                LD H, A
                INC A
                JP Z, @Music.FinishChannelB.UpdateGate                          ; переход, если состояние канала равно FF, передать нулевую амплитуду без чтения ресурсов

                ; чтение циклического заголовка сэмпла через временный SP
                LD SP, #0000
                POP DE
                LD A, #00
                LD L, A
                INC A
                ; проверка следующей позиции сэмпла относительно FMusicLoopHeader.Length
                CP D
                JR C, @Music.RenderChannelB.StoreSamplePos                      ; переход, если следующая позиция сэмпла меньше Length, сохранить её без зацикливания

                LD A, E
                ; сохранение следующей позиции сэмпла, текущий шаг адресуется по прежней позиции
StoreSamplePos: LD (@MusicChannelBState.SampleCursor), A
                ; расчёт смещения шага, второе удвоение затрагивает только L и теряет перенос
                ADD HL, HL
                SLA L
                ADD HL, SP
                LD SP, HL
                POP DE
                LD A, D
                OR @MusicSampleConst.HighNibbleMask
                LD L, A
                LD A, E
                ADD A, A
                LD A, #00
                JR NC, @Music.RenderChannelB.ApplyBias                          ; переход, если AdjustBit равен нулю, сохранить поправку уровня

                JP M, @Music.RenderChannelB.LimitAdjust                         ; переход, если AdjustUpBit установлен, увеличивать поправку до 31

                SUB #01
                JR @Music.RenderChannelB.StoreAdjust

                ; ограничение увеличения поправки уровня сравнением с 31
LimitAdjust:    CP @MusicSampleConst.MaxAdjust
                ; учёт переноса для увеличения либо подавления выхода за нулевую поправку
StoreAdjust:    ADC A, #00
                LD (@MusicChannelBRow.AmplitudeAdjust), A
                ; расчёт уровня как базового значения плюс поправка минус 16
ApplyBias:      ADD A, L
                JR C, @Music.RenderChannelB.ClampLevel                          ; переход, если базовый уровень с поправкой не меньше 16, проверить верхний предел

                XOR A
                ; ограничение уровня диапазоном 0..15
ClampLevel:     CP @MusicSampleConst.NibbleBoundary
                JR C, @Music.RenderChannelB.ScaleVolume                         ; переход, если уровень меньше 16, применить строку таблицы

                LD A, @MusicSampleConst.MaxLevel
                ; применение строки исходной таблицы громкости через байтовое смещение
ScaleVolume:    ADD A, #00
                LD L, A
                LD H, @MusicSampleConst.VolumePage
                LD A, (HL)
                SRL E
                JR C, @Music.RenderChannelB.SaveLevel                           ; переход, если FixedLevelBit установлен, сохранить уровень без добавления маски огибающей

                OR #00
                ; сохранение рассчитанного уровня и его флагов в альтернативном AF
SaveLevel:      EX AF, AF'
                LD A, D
                RLCA
                JR C, @Music.RenderChannelB.EnvelopeDelta                       ; переход, если EnvShiftBit установлен, рассчитать вклад огибающей

                LD A, #00
                ADD A, E
                ; проверка AccumShiftBit, нужно ли сохранять вклад для следующих кадров
                BIT @MusicSampleConst.AccumShiftBit, D
                JR Z, @Music.RenderChannelB.SetNoise                            ; переход, если AccumShiftBit равен нулю, использовать вклад только в текущем кадре

                LD (@MusicChannelBRow.NoiseAccum), A
                ; замена текущего вклада шума значением канала B
SetNoise:       LD IXH, A
                JR @Music.RenderChannelB.MixerBits

                ; расширение знака пятибитового вклада огибающей
EnvelopeDelta:  LD A, E
                AND @MusicSampleConst.ShiftMask
                CP @MusicSampleConst.NibbleBoundary
                JR C, @Music.RenderChannelB.AddEnvelopeBias                     ; переход, если пятибитовый вклад меньше 16, сохранить неотрицательное значение

                OR @MusicSampleConst.HighNibbleMask
                ; прибавление накопленного вклада огибающей по модулю 256
AddEnvelopeBias:ADD A, #00
                ; проверка AccumShiftBit, нужно ли сохранять вклад для следующих кадров
                BIT @MusicSampleConst.AccumShiftBit, D
                JR Z, @Music.RenderChannelB.AddToEnvelope                       ; переход, если AccumShiftBit равен нулю, использовать вклад только в текущем кадре

                LD (@MusicChannelBRow.EnvelopeAccum), A
                ; добавление вклада канала к общему восьмибитовому периоду в альтернативном L
AddToEnvelope:  EXX
                ADD A, L
                LD L, A
                EXX
                ; формирование битов текущего канала в микшере
MixerBits:      LD A, D
                RRCA
                RRCA
                RRCA
                AND @MusicSampleConst.MixerMaskB
                OR IXL
                LD IXL, A
                POP BC
                LD HL, #0000
                ADD HL, BC
                ; проверка AccumToneBit, нужно ли сохранять тональную поправку
                BIT @MusicSampleConst.AccumToneBit, D
                JR Z, @Music.RenderChannelB.ReadOrnament                        ; переход, если AccumToneBit равен нулю, оставить прежний накопитель тона

                LD (@MusicChannelBRow.ToneAccum), HL
                ; сохранение текущей тональной поправки в DE и переход к заголовку орнамента
ReadOrnament:   EX DE, HL
                ; чтение циклического заголовка орнамента через временный SP
                LD SP, #0000
                POP BC
                LD A, #00
                LD L, A
                INC A
                ; проверка следующей позиции орнамента относительно FMusicLoopHeader.Length
                CP B
                JR C, @Music.RenderChannelB.StoreOrnPos                         ; переход, если следующая позиция орнамента меньше Length, сохранить её без зацикливания

                LD A, C
                ; сохранение следующей позиции орнамента, текущий байт ещё берётся по прежней
StoreOrnPos:    LD (@MusicChannelBState.OrnamentCursor), A
                LD H, #00
                ADD HL, SP
                LD A, (@MusicChannelBRow.CurrentNote)
                ; расчёт байтовой суммы текущей ноты и орнамента с оборачиванием
                ADD A, (HL)
                ADD A, A
                JR NC, @Music.RenderChannelB.ReadPitch                          ; переход, если байтовая сумма ноты и орнамента меньше 128, использовать её индекс

                XOR A
                ; выбор слова периода по индексу ноты, SP временно указывает на таблицу
ReadPitch:      LD L, A
                LD H, @MusicSampleConst.PitchPage
                LD SP, HL
                POP HL
                ADD HL, DE
                ; чтение прежнего накопленного смещения тона перед записью периода
                LD BC, #0000
                ADD HL, BC
                ; запись периода текущего канала до обновления шага скольжения
                LD (#DC02), HL
                LD A, #00
                ; расчёт уменьшенного счётчика тонального скольжения
                DEC A
                JP M, @Music.FinishChannelB.RestoreLevel                        ; переход, если результат DEC счётчика скольжения отрицателен, оставить его без записи

                JR NZ, @Music.FinishChannelB.StoreSlideDelay                    ; переход, если уменьшенный счётчик ненулевой, сохранить его без добавления шага

                EX DE, HL
                ; чтение слова шага и прибавление к прежнему SlideOffset
                LD HL, #0000
                ADD HL, BC
                ; сохранение нового накопленного смещения, текущий тон уже записан
                LD (@MusicChannelBRow.SlideOffset), HL
                JR @Music.FinishChannelB.Entry

                ; расчёт периода для проверки достижения цели с уже обновлённым смещением
LimitTarget:    ADD HL, DE
                EX DE, HL
                ; чтение целевой ноты для получения её слова периода
                LD A, #00
                LD L, A
                ADD HL, HL
                LD H, @MusicSampleConst.PitchPage
                LD SP, HL
                POP HL
                ; проверка направления по целевой и текущей нотам
                CP #00
                JR NC, @Music.RenderChannelB.CompareLimit                       ; переход, если целевая нота не меньше текущей, вычитать расчётный период из целевого

                EX DE, HL
                ; сравнение расчётного и целевого периодов с учётом направления из CP
CompareLimit:   SBC HL, DE
                JR C, @Music.FinishChannelB.Entry                               ; переход, если вычитание дало заём, продолжить скольжение с перезагрузкой

                ; замена текущей ноты целевой после достижения ограничения
                LD (@MusicChannelBRow.CurrentNote), A
                XOR A
                LD L, A
                ; сохранение старшего байта разности с нулевым младшим после достижения цели
                LD (@MusicChannelBRow.SlideOffset), HL
                JR @Music.FinishChannelB.StoreSlideDelay

                endmodule
                endmodule
