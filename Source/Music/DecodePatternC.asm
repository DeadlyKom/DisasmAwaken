                module Music
                module DecodePatternC
                ; Документация [декодирование паттернов](../../Docs/MusicPattern.md)
                ; -----------------------------------------
                ; Декодирование строки C с непосредственным сбросом новой ноты и отложенными эффектами
                ; исходная запись 10, файловые смещения #0A83..#0B0B
                ; In:
                ;   HL задаёт страницу H таблиц указателей, штатный вызов начинает с H=DB, L первоначально произволен
                ;   DE указывает команду строки и последующие параметры отложенных эффектов, BC заменяется на 1020
                ;   AF входных аргументов не задаёт, на CPU-стеке находится внешний возврат и есть место для двух байтов на каждый эффект
                ;   HL', DE' и BC' содержат подготовительные маркеры A/B, D' переносится в H', B' либо E' соответствующими командами
                ;   строка конечна и завершается нотой 50..AF, выключением C0 либо D0, отложенные команды используют коды 1..5, 8, 9
                ;   код и изменяемые операнды MUZ1 доступны для записи, прерывания запрещены
                ; Out:
                ;   DE указывает первый байт после терминальной команды и параметров всех исполненных отложенных эффектов
                ;   параметры ноты, громкости, огибающей, сэмпла и орнамента изменены согласно таблице команд MusicPattern.md
                ;   эффекты исполняются в обратном порядке команд через RET, их байтовые параметры читаются подряд после терминатора
                ;   без эффектов BC=0120 после ноты, BC=1020 после C0 либо D0
                ;   без эффектов AF=1044 после ноты, FFBB после C0, 0041 после D0, HL=0 после ноты
                ;   последний исполненный эффект уточняет HL, BC и AF согласно MusicEffects.md, например portamento задаёт B=0
                ;   AF', IX, IY, I, IM и IFF сохраняются, SP после внешнего RET равен входному SP+2
                ;   все альтернативные пары сохраняются
                ; Corrupt:
                ;   HL, DE, BC, AF
                ;   изменяемые параметры выбранного канала, общая огибающая, шум B, темп, память отложенного стека, R
                ; Note:
                ;   реальные адреса и все внутренние входы приведены в MusicPattern.md, общие хвосты находятся в соседнем PatternCommands
                ;   поиск указателя использует текущий H и оборачивание L, после эффекта H может стать страницей адреса обработчика
                ;   коды 0, 6, 7 и 10..15 тоже читают слова и помещают их в стек, их выполнение не входит в доказанный контракт
                ;   проверка полных строк не доказывает корректность произвольного повреждённого потока или нативного звука
                ; -----------------------------------------
                ; подготовка шагов порогового декодирования, B=10 и C=20
Entry:          LD BC, #1020
ReadCommand:    LD A, (DE)
                INC DE
                ; проверка исходного диапазона F0..FF добавлением с переносом
                ADD A, B
                JR C, @Music.PatternCommandsC.OrnamentSample                    ; переход, если исходный код F0..FF, выбрать совместную команду сэмпла и орнамента

                ; проверка исходного диапазона D0..EF добавлением с переносом
                ADD A, C
                JR C, @Music.DecodePatternC.SampleOrEnd                         ; переход, если исходный код D0..EF, выбрать сэмпл либо завершение строки

                ; проверка исходного диапазона C0..CF добавлением с переносом
                ADD A, B
                JR C, @Music.PatternCommandsC.Entry                             ; переход, если исходный код C0..CF, выбрать громкость либо выключение ноты

                ; проверка исходного диапазона B0..BF добавлением с переносом
                ADD A, B
                JR C, @Music.DecodePatternC.EnvelopeOrDelay                     ; переход, если исходный код B0..BF, выбрать подкоманду огибающей либо задержки

                ; проверка исходного диапазона 50..AF добавлением с переносом
                ADD A, #60
                JR C, @Music.DecodePatternC.SetNote                             ; переход, если исходный код 50..AF, выбрать ноту

                ; проверка исходного диапазона 40..4F добавлением с переносом
                ADD A, B
                JR C, @Music.DecodePatternC.SetOrnament                         ; переход, если исходный код 40..4F, выбрать орнамент

                ; проверка исходного диапазона 10..3F добавлением с переносом
                ADD A, #30
                JR C, @Music.DecodePatternC.EnvelopeSample                      ; переход, если исходный код 10..3F, выбрать совместную команду огибающей и сэмпла

                ; расчёт младшего адреса отложенного обработчика, таблица пересекается с исходным кодом
                LD HL, @MusicPatternState.RowCounterA
                RLA
                ADD A, L
                LD L, A
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                ; помещение адреса отложенного обработчика в стек, он будет исполнен последующим RET после окончания строки
                PUSH HL
                ; сохранение текущей ноты C для последующей отложенной команды скольжения
                LD A, (@MusicEffectState.CurrentNoteC)
                LD (@MusicEffectState.PreviousNoteC), A
                JR @Music.DecodePatternC.ReadCommand

EnvelopeOrDelay:JR Z, @Music.PatternCommandsC.StoreEnvelope                     ; переход, если код огибающей равен нулю, снять её маску по команде B0

                ; проверка кода B1 после уменьшения, ноль означает чтение длительности строки
                DEC A
                JR NZ, @Music.PatternCommandsC.ReadEnvelope                     ; переход, если код после DEC ненулевой, прочитать форму и период огибающей для B2..BF

                ; чтение новой перезагрузки счётчика строки без нормализации нулевого значения
                LD A, (DE)
                LD (@MusicPatternState.RowDelayC), A
                INC DE
                JR @Music.DecodePatternC.ReadCommand

EnvelopeSample: JR Z, @Music.PatternCommandsC.EnvelopeSample                    ; переход, если код совместной команды равен нулю, выбрать сэмпл со снятой маской огибающей

                ; запись формы общей огибающей и чтение периода старшим байтом вперёд
                LD (@MusicEnvelopeState.Shape), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (@MusicEnvelopeState.Base), A
                LD A, #10
                JR @Music.PatternCommandsC.EnvelopeSample

SampleOrEnd:    RET Z                                                           ; выход, если преобразованный код сэмпла равен нулю, завершить строку по команде D0

                ; расчёт удвоенного индекса сэмпла из команды D1..EF
                ADD A, A
                JR @Music.PatternCommandsC.StoreSample

                ; расчёт адреса указателя орнамента, текущая страница H сохраняется
SetOrnament:    ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (@MusicSynthesisC.OrnamentPointer), BC
                XOR A
                LD (@MusicEffectState.OrnamentCursorC), A
                JR @Music.DecodePatternC.Entry

                ; перенос текущей ноты C с непосредственным сбросом курсоров, накопителей и счётчиков
SetNote:        LD (@MusicEffectState.CurrentNoteC), A
                XOR A
                LD H, A
                LD L, A
                LD (@MusicEffectState.SampleCursorC), A
                LD (@MusicSynthesisC.NoiseAccum), A
                LD (@MusicSynthesisC.EnvelopeAccum), A
                LD (@MusicEffectState.OrnamentCursorC), A
                LD (@MusicState.SlideCounterC), A
                LD (@MusicGateState.StateC), A
                LD (@MusicState.GateCounterC), A
                LD (@MusicSynthesisC.ToneAccum), HL
                ; возврат поправки уровня C к нейтральному значению 10
                LD A, #10
                LD (@MusicSynthesisC.AmplitudeAdjust), A
                LD B, #01
                RET

                endmodule
                endmodule
