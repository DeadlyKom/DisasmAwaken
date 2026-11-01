                module Music
                module PatternCommandsC
                ; Документация [декодирование паттернов](../../Docs/MusicPattern.md)
                ; -----------------------------------------
                ; Внутренние входы громкости, выключения, огибающей и указателей канала C
                ; исходная запись 10, файловые смещения #0A3D..#0A82
                ; In:
                ;   HL задаёт текущую страницу таблицы указателей, DE указывает следующие данные команды, BC=1020 на входах из декодера
                ;   AF содержит преобразованный код и флаги выбора диапазона, точные значения для каждого входа приведены в MusicPattern.md
                ;   HL', DE' и BC' содержат подготовительные маркеры, AF' сохраняется
                ;   внутренние входы допустимы только при условиях соответствующей ветви DecodePatternC
                ;   стек содержит внешний возврат и уже помещённые обработчики, банк доступен для записи, прерывания запрещены
                ; Out:
                ;   Entry выбирает громкость либо выключение C по флагу Z
                ;   SetVolume с ненулевым кодом сохраняет (A*16)&FF и продолжает ReadCommand, нулевой код выключает ноту через RET
                ;   ReadEnvelope записывает форму A, старший и младший байты периода из DE и устанавливает маску 10
                ;   StoreEnvelope переносит маску A и продолжает чтение, у A/B также B′=D′
                ;   OrnamentSample читает указатель орнамента по младшему индексу, снимает маску, затем читает сырой индекс сэмпла из потока
                ;   EnvelopeSample записывает маску, у C обнуляет позицию орнамента, затем выбирает сэмпл
                ;   StoreSample получает в A уже удвоенный индекс, читает слово в текущей странице H со смещением A0+A
                ;   после StoreSample исполнение продолжается в Entry декодера с восстановлением BC=1020, отдельного CALL нет
                ;   выходы с RET могут запускать отложенные обработчики, полные конечные выходы определяет договор DecodePatternC
                ; Corrupt:
                ;   HL, DE, BC, AF
                ;   перечисленные параметры канала и общей огибающей, R
                ; Note:
                ;   файл объединяет несколько внутренних входов одной процедуры декодирования, самостоятельного универсального CALL-контракта нет
                ;   все входы и общие хвосты проверены в составе исходного декодера, отдельные произвольные состояния вне его условий не заявлены
                ; -----------------------------------------
Entry:          JR Z, @Music.PatternCommandsC.ReleaseNote                       ; переход, если код громкости равен нулю, выключить ноту по команде C0

                ; расчёт байтового смещения строки громкости, код 1..15 умножается на 16
                ADD A, A
                ADD A, A
                ADD A, A
                ADD A, A
                LD (@MusicSynthesisC.VolumeOffset), A
                JR @Music.DecodePatternC.ReadCommand

                ; выключение C, счётчик чередования получает ноль, Disabled получает FF
ReleaseNote:    LD (@MusicState.GateCounterC), A
                DEC A
                LD (@MusicGateState.StateC), A
                RET

                ; запись формы общей огибающей и чтение периода старшим байтом вперёд
ReadEnvelope:   LD (@MusicEnvelopeState.Shape), A
                LD A, (DE)
                INC DE
                LD (#DF51), A
                LD A, (DE)
                INC DE
                LD (@MusicEnvelopeState.Base), A
                LD A, #10
                ; перенос маски огибающей C без сброса позиции орнамента
StoreEnvelope:  LD (@MusicSynthesisC.EnvelopeMask), A
                JR @Music.DecodePatternC.ReadCommand

                ; расчёт адреса указателя орнамента, текущая страница H сохраняется
OrnamentSample: ADD A, A
                ADD A, #E0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (@MusicSynthesisC.OrnamentPointer), BC
                XOR A
                ; перенос маски огибающей C и сброс позиции орнамента перед выбором сэмпла
EnvelopeSample: LD (@MusicSynthesisC.EnvelopeMask), A
                XOR A
                LD (@MusicEffectState.OrnamentCursorC), A
                LD A, (DE)
                INC DE
                ; расчёт адреса указателя сэмпла, входной индекс уже удвоен, перенос из L в H исключён
StoreSample:    ADD A, #A0
                LD L, A
                LD C, (HL)
                INC L
                LD B, (HL)
                LD (@MusicSynthesisC.SamplePointer), BC
                ; JP @Music.DecodePatternC.Entry, продолжение в DecodePatternC.asm

                endmodule
                endmodule
