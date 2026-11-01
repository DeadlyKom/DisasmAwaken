                module Music
                module InitializeModule
                ; Документация [инициализация и глушение AY](../../Docs/MusicInitialization.md)
                ; -----------------------------------------
                ; Перенос полей модуля, 48 указателей и начальных состояний с восстановлением SP и глушением AY
                ; исходная запись 10, файловые смещения #000A..#007B
                ; In:
                ;   HL указывает базу модуля, доступны байты задержки, числа позиций, петли, таблицы паттернов и 48 относительных слов
                ;   DE, BC и AF аргументов не задают, на CPU-стеке находится внешний возврат
                ;   заголовок и читаемые 201 байт не перекрываются с кодом проигрывателя и целями его записей
                ;   банк MUZ1 доступен для записи, временное чтение через SP не прерывается, DI выполняется первой командой InitializeModule
                ; Out:
                ;   HL=DC10, DE=0000, BC=BFFD, AF=FF43, SP после внешнего RET равен входному SP+2
                ;   SavedStack хранит входной SP, ModuleBase хранит базу модуля, RowTempo получает байт 100
                ;   PositionCursor=база+201, LoopPosition=база+201+байт 102, PatternTable=база+слово 103, суммы по модулю 65536
                ;   48 слов со смещений 105..200 преобразованы добавлением базы и записаны в DBA0..DBFF
                ;   RowCounterA/B/C=1, EntryOpcodeA=01, маски огибающей A/B/C=0
                ;   указатели орнаментов A/B/C, ожидающие сэмплы A/B, текущий сэмпл C и PatternA получают DC10
                ;   ожидающие строки громкости A/B и VolumeOffset C получают F0, Disabled A/B/C получают FF
                ;   аппаратные AY 13..0 обнулены в точном порядке, 28 OUT через FFFD и BFFD, буфер AY в RAM сохранён
                ;   HL', DE', BC', AF', IX, IY, I и IM сохраняются, IFF сброшено и на выходе не разрешается
                ; Corrupt:
                ;   HL, DE, BC, AF, IFF, SavedStack, перечисленные указатели и начальные состояния, аппаратные AY, R
                ; Note:
                ;   это частичная инициализация, курсоры, накопители и прочие изменяемые операнды не восстанавливаются из исходных байтов
                ;   POP AF читает PositionCount в F и LoopIndex в A, окончательный F не зависит от этих данных
                ;   слово 0101 по DE1E одновременно задаёт счётчик A и код 01 следующей инструкции входа тика
                ;   DC10 является также началом первой физической строки громкости, отдельной области пустого сэмпла нет
                ;   временный SP восстанавливается до очистки аппаратных регистров, подробности MusicInitialization.md
                ; -----------------------------------------
                ; запрет IRQ перед использованием SP для чтения заголовка и относительных указателей
Entry:          DI
                ; сохранение обычного SP в операнде команды его последующего восстановления
                LD (@MusicInitializeState.SavedStack), SP
                ; сохранение базы модуля для перевода относительных указателей паттернов
                LD (@MusicAdvanceAState.ModuleBase), HL
                ; сохранение базы в BC для преобразования 48 относительных указателей данных
                LD B, H
                LD C, L
                ; расчёт адреса поля RowTempo со смещением FMusicModuleHeader.RowTempo
                LD DE, FMusicModuleHeader.RowTempo
                ADD HL, DE
                LD A, (HL)
                INC HL
                LD (@MusicEnvelopeState.RowTempo), A
                ; переключение SP на поле PositionCount и расчёт адреса списка позиций
                LD SP, HL
                ADD HL, DE
                LD (@MusicAdvanceAState.PositionCursor), HL
                ; чтение PositionCount в F и LoopIndex в A, это данные заголовка, а не сохранённый AF
                POP AF
                ; расчёт указателя петли от начала списка по байтовому LoopIndex
                LD E, A
                ADD HL, DE
                LD (@MusicAdvanceAState.LoopPosition), HL
                ; преобразование относительного адреса таблицы троек паттернов в абсолютный
                POP HL
                ADD HL, BC
                LD (@MusicAdvanceAState.PatternTable), HL
                ; выбор физической таблицы 32 указателей сэмплов и 16 указателей орнаментов
                LD HL, @MusicDataPointers.Sample00
                ; чтение очередного относительного слова через SP и прибавление базы модуля
CopyDataPointer:EX DE, HL
                POP HL
                ADD HL, BC
                EX DE, HL
                ; запись абсолютного слова в текущую запись FMusicDataPointer
                LD (HL), E
                INC L
                LD (HL), D
                INC L
                JR NZ, @Music.InitializeModule.CopyDataPointer                  ; переход, если младший адрес после записи слова ненулевой, продолжить заполнение DBA0..DBFF

                ; расчёт слова 0101 из завершившего цикл L=00 для трёх счётчиков и кода входа A
                INC L
                LD H, L
                LD (@MusicPatternState.RowCounterA), HL
                LD (@MusicPatternState.RowCounterB), HL
                ; снятие маски огибающей трёх каналов без очистки остальных накопителей
                XOR A
                LD (@MusicSynthesisA.EnvelopeMask), A
                LD (@MusicChannelBRow.EnvelopeMask), A
                LD (@MusicSynthesisC.EnvelopeMask), A
                ; восстановление обычного SP после 48 слов заголовка
                LD SP, #0000
                ; назначение исходного пустого состояния по адресу Volume01, физические данные не дублируются
                LD HL, @MusicVolumes.Volume01
                LD (@MusicSynthesisA.OrnamentPointer), HL
                LD (@MusicChannelBRow.OrnamentPointer), HL
                LD (@MusicSynthesisC.OrnamentPointer), HL
                LD (@MusicChannelARow.PendingSample), HL
                LD (@MusicChannelBRow.PendingSample), HL
                LD (@MusicSynthesisC.SamplePointer), HL
                LD (@MusicAdvanceAState.PatternA), HL
                ; расчёт начального смещения громкости F0 вычитанием 10 из нулевого A
                SUB #10
                LD (@MusicChannelARow.VolumeRow), A
                LD (@MusicChannelBRow.VolumeRow), A
                LD (@MusicSynthesisC.VolumeOffset), A
                ; расчёт выключенного состояния FF через SBC A, A с Carry предыдущего SUB
                SBC A, A
                LD (@MusicGateState.StateA), A
                LD (@MusicGateState.StateC), A
                LD (@MusicChannelBRow.Disabled), A
                ; JP @Music.ClearAyRegisters.Entry, продолжение в ClearAyRegisters.asm

                endmodule
                endmodule
