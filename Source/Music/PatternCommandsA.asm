                module Music
                module PatternCommandsA
                ; Документация [декодирование паттернов](../../Docs/MusicPattern.md)
                ; -----------------------------------------
                ; Внутренние входы нот, громкости, огибающей и выбора сэмпла и орнамента A
                ; исходная запись 10, файловые смещения #08DC..#0938
                ; In:
                ;   HL задаёт текущую страницу таблицы указателей, DE указывает следующие данные команды, BC=1020 на входах из декодера
                ;   AF содержит преобразованный код и флаги выбора диапазона, точные значения для каждого входа приведены в MusicPattern.md
                ;   HL', DE' и BC' содержат подготовительные маркеры, AF' сохраняется
                ;   внутренние входы допустимы только при условиях соответствующей ветви DecodePatternA
                ;   стек содержит внешний возврат и уже помещённые обработчики, банк доступен для записи, прерывания запрещены
                ; Out:
                ;   Entry переносит A в ожидающую ноту, задаёт код NOP разрешения, B=1, A=0, F=44 и H′=D′
                ;   SetVolume с ненулевым кодом сохраняет (A*16)&FF и продолжает ReadCommand, нулевой код выключает ноту через RET
                ;   ReadEnvelope записывает форму A, старший и младший байты периода из DE и устанавливает маску 10
                ;   StoreEnvelope переносит маску A и продолжает чтение, у A/B также B′=D′
                ;   OrnamentSample читает указатель орнамента по младшему индексу, снимает маску, затем читает сырой индекс сэмпла из потока
                ;   EnvelopeSample записывает маску, у C обнуляет позицию орнамента, затем выбирает сэмпл
                ;   StoreSample получает в A уже удвоенный индекс, читает слово в текущей странице H со смещением A0+A
                ;   после StoreSample исполнение продолжается в Entry декодера с восстановлением BC=1020, отдельного CALL нет
                ;   выходы с RET могут запускать отложенные обработчики, полные конечные выходы определяет договор DecodePatternA
                ; Corrupt:
                ;   HL, DE, BC, AF, H', B'
                ;   перечисленные параметры канала и общей огибающей, R
                ; Note:
                ;   файл объединяет несколько внутренних входов одной процедуры декодирования, самостоятельного универсального CALL-контракта нет
                ;   все входы и общие хвосты проверены в составе исходного декодера, отдельные произвольные состояния вне его условий не заявлены
                ; -----------------------------------------
                ; перенос преобразованного индекса ноты в ожидающий параметр, подготовка признака новой ноты
Entry:          LD (@MusicChannelARow.PendingNote), A
                XOR A
                LD B, #01
                JR @Music.PatternCommandsA.StoreEnable

SetVolume:      JR Z, @Music.PatternCommandsA.ReleaseNote                       ; переход, если код громкости равен нулю, выключить ноту по команде C0

                ; расчёт байтового смещения строки громкости, код 1..15 умножается на 16
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                LD (@MusicChannelARow.VolumeRow), A
                JR @Music.DecodePatternA.ReadCommand

                ; подготовка кода CPL для выключения канала при следующем переносе строки
ReleaseNote:    LD A, #2F
                ; сохранение NOP либо CPL и установка маркера переноса ноты H′=D′
StoreEnable:    LD (@MusicChannelARow.EnableCode), A
                EXX
                LD H, D
                EXX
                RET

EnvelopeOrDelay:JR Z, @Music.PatternCommandsA.StoreEnvelope                     ; переход, если код огибающей равен нулю, снять её маску по команде B0

                ; проверка кода B1 после уменьшения, ноль означает чтение длительности строки
                DEC A
                JR NZ, @Music.PatternCommandsA.ReadEnvelope                     ; переход, если код после DEC ненулевой, прочитать форму и период огибающей для B2..BF

                ; чтение новой перезагрузки счётчика строки без нормализации нулевого значения
                LD A, (DE)
                LD (@MusicPatternState.RowDelayA), A
                INC DE
                JR @Music.DecodePatternA.ReadCommand

                ; запись формы общей огибающей и чтение периода старшим байтом вперёд
ReadEnvelope:   LD (@MusicEnvelopeState.Shape), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (@MusicEnvelopeState.Base), A
                LD A, #10
                ; сохранение маски огибающей и установка маркера переноса орнамента B′=D′
StoreEnvelope:  LD (@MusicChannelARow.PendingEnvelope), A
                EXX
                LD B, D
                EXX
                JR @Music.DecodePatternA.ReadCommand

                ; расчёт адреса указателя орнамента, текущая страница H сохраняется
OrnamentSample: ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (@MusicChannelARow.PendingOrnament), BC
                XOR A
                ; перенос маски огибающей, подготовка орнамента и чтение сырого индекса сэмпла
EnvelopeSample: LD (@MusicChannelARow.PendingEnvelope), A
                EXX
                LD B, D
                EXX
                LD A, (DE)
                INC DE
                ; расчёт адреса указателя сэмпла, входной индекс уже удвоен, перенос из L в H исключён
StoreSample:    ADD A, #A0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (@MusicChannelARow.PendingSample), BC
                ; JP @Music.DecodePatternA.Entry, продолжение в DecodePatternA.asm

                endmodule
                endmodule
