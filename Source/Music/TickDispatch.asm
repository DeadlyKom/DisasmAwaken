                module Music
                module TickDispatch
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Изменяемый вход тика, выбор синтеза либо перенос подготовленных параметров строки A
                ; исходная запись 10, файловые смещения #031F..#038F
                ; In:
                ;   HL, DE и BC при EntryOpcode=01 переходят в альтернативные пары, исходный BC заменяется адресом DFE3 до EXX
                ;   AF входных аргументов не задаёт, EntryOpcode содержит C3 либо 01
                ;   HL', DE' и BC' после EXX становятся рабочими, исходные HL' и DE' затем замещаются подготовкой
                ;   NoteBlock, OrnamentBlock и SlideBlock содержат 18 либо 06, EnableCode содержит 00 либо 2F, ResetOpcode содержит 22 либо 01
                ;   параметры строки уже подготовлены в доступном для записи банке MUZ1, прерывания запрещены
                ; Out:
                ;   при EntryOpcode=C3 выполнен только JP в RenderChannelA, пары регистров, IX/IY, SP, I/IM/IFF и память до этой границы сохранены, R получает один M1
                ;   при EntryOpcode=01 выполнен LD BC,DFE3 и EXX, EntryOpcode восстановлен в C3, продолжение в StageGateAndSampleA по DE90
                ;   HL равен последнему применённому указателю сэмпла, орнамента либо шагу скольжения, иначе HL=0
                ;   DE=0618
                ;   B изначально равен входному B', либо #E0 при ResetOpcode=01, затем #29 после ноты, #0F после орнамента, #1C после скольжения
                ;   C равен входному C', либо #98 при ResetOpcode=01
                ;   A равен VolumeRow, затем PendingEnvelope при ветви орнамента, затем 0 при ветви скольжения
                ;   F=7E только при включённом NoteBlock с CPL и выключенных орнаменте и скольжении, иначе F=44
                ;   HL' и DE' равны исходным HL и DE, BC'=DFE3, AF', IX, IY, SP, I, IM и IFF сохранены
                ;   ResetOpcode=22 обнуляет SlideOffset, 01 сохраняет его, промежуточный BC=E098 затем уточняется включёнными блоками
                ;   VolumeRow всегда переносится в VolumeOffset, NoteBlock=06 сбрасывает курсоры, накопители и счётчики канала A
                ;   ветвь ноты задаёт Disabled=0 при NOP либо FF при CPL, CurrentNote, SamplePointer и AmplitudeAdjust=10
                ;   OrnamentBlock=06 обнуляет OrnamentCursor, устанавливает OrnamentPointer и EnvelopeMask
                ;   SlideBlock=06 устанавливает TargetNote, SlideCounter, SlideReload, SlideStep и SlideBranch, GateCounter=0
                ;   подготовка строки требует 14+15*n+6*o+11*s M1, индикаторы включённых блоков определены в Note, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC' при подготовке строки, перечисленные поля, EntryOpcode, R
                ;   при прямом JP перечисленные пары сохраняются, R получает один M1 до начала RenderChannelA
                ; Note:
                ;   ApplyRow является внутренним входом после изменяемой трёхбайтовой команды, это не отдельная вызываемая процедура
                ;   три кода пропуска блоков здесь не сбрасываются, их меняет декодер паттерна
                ;   SlideBranch=00 включает ограничение целевой нотой, 1D обходит его, эта ветвь исполняется позднее в синтезе
                ;   собственного RET нет, договор заканчивается перед StageGateAndSampleA либо перед RenderChannelA
                ;   алгоритм подготовки и проверка двух режимов описаны в MusicChannelStaging.md
                ;   n, o, s равны 1 при коде 06 соответствующего NoteBlock, OrnamentBlock, SlideBlock, иначе 0 при коде 18
                ; -----------------------------------------
                ; изменяемый вход, C3 выполняет JP к синтезу, 01 превращает те же байты в LD BC,DFE3
Entry:          JP @Music.RenderChannelA.Entry

                ; переключение на подготовленный декодером комплект регистров перед применением строки A
ApplyRow:       EXX
                ; восстановление прямого входа к синтезу для следующего тика
                LD A, #C3
                LD (@MusicChannelARow.EntryOpcode), A
                ; подготовка нулевого HL для сбросов и пары DE с кодами пропуска и включения блоков
                XOR A
                LD L, A
                LD H, A
                LD DE, #0618
                ; изменяемая команда, 22 обнуляет SlideOffset, 01 загружает BC адресом E098 без записи
                LD (@MusicSynthesisA.SlideOffset), HL
                ; изменяемый JR пропускает сброс ноты, код 06 включает тело и загружает B длиной 29
                JR @Music.TickDispatch.ApplyVolume

                ; сброс курсоров сэмпла и орнамента, накопителей шума и огибающей, счётчиков скольжения и чередования
                LD (@MusicChannelAState.SampleCursor), A
                LD (@MusicSynthesisA.NoiseAccum), A
                LD (@MusicSynthesisA.EnvelopeAccum), A
                LD (@MusicChannelAState.OrnamentCursor), A
                LD (@MusicSynthesisA.SlideCounter), A
                LD (@MusicChannelAState.GateCounter), A
                ; сброс накопленной тональной поправки сэмпла
                LD (@MusicSynthesisA.ToneAccum), HL
                ; изменяемый NOP оставляет ноль для включения A, CPL создаёт выключенное состояние FF
                CPL
                LD (@MusicGateState.StateA), A
                ; перенос ожидающего индекса ноты в текущую ноту синтеза A
                LD A, #00
                LD (@MusicEffectState.CurrentNoteA), A
                ; перенос ожидающего указателя сэмпла
                LD HL, #0000
                LD (@MusicSynthesisA.SamplePointer), HL
                ; возврат поправки уровня к нейтральному значению 10
                LD A, #10
                LD (@MusicSynthesisA.AmplitudeAdjust), A
                ; перенос смещения строки громкости независимо от наличия новой ноты
ApplyVolume:    LD A, #00
                LD (@MusicSynthesisA.VolumeOffset), A
                ; изменяемый JR пропускает подготовку орнамента, код 06 включает тело
                JR @Music.TickDispatch.ApplySlide

                ; сброс позиции орнамента перед переносом его нового указателя
                XOR A
                LD (@MusicChannelAState.OrnamentCursor), A
                ; перенос ожидающего указателя орнамента
                LD HL, #0000
                LD (@MusicSynthesisA.OrnamentPointer), HL
                ; перенос ожидаемой маски огибающей в расчёт амплитуды A
                LD A, #00
                LD (@MusicSynthesisA.EnvelopeMask), A
                ; изменяемый JR пропускает настройку скольжения, код 06 включает тело
ApplySlide:     JR @Music.StageGateAndSampleA.Entry

                ; перенос ожидающей целевой ноты ограниченного скольжения
                LD A, #00
                LD (@MusicSynthesisA.TargetNote), A
                ; запуск задержки шага вместе с установкой её перезагрузки
                LD A, #00
                LD (@MusicSynthesisA.SlideCounter), A
                LD (@MusicSynthesisA.SlideReload), A
                ; перенос знакового слова шага скольжения A
                LD HL, #0000
                LD (@MusicSynthesisA.SlideStep), HL
                ; перенос смещения JR, выбирающего ограничение целевой нотой либо его обход
                LD A, #00
                LD (@MusicSynthesisA.SlideBranch), A
                ; отключение текущего чередования разрешения при подготовке скольжения
                XOR A
                LD (@MusicChannelAState.GateCounter), A
                ; JP @Music.StageGateAndSampleA.Entry, продолжение в StageGateAndSampleA.asm

                endmodule
                endmodule
