                module Station
                module Interrupt
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [прерывание, отдельный стек и восстановление цепочки RET](../../Docs/StationInterrupt.md)
; -----------------------------------------
; Обслуживание ввода, указателя, музыки и BCD-счётчика с восстановлением CPU-контекста и стека рисователя
; исходная запись 4, файловые смещения #3AEA..#3C12
; In:
;   на CPU-стеке уже сохранён аппаратный адрес продолжения, оба байта доступны до смены SP
;   исходный SP не пересекает собственное хранилище ISR #9C13..#9C42 и исполняемый код обработчика
;   тень CurrentPage соответствует доступному аппаратному режиму, блокировка #7FFD.bit5 снята
;   выполняются договоры PollJoystick,PollKeys,PollMouse и UpdatePointer при разрешённой ветви
;   для MusicMode=#81 инициализирован PlayFrame в банке 3, его возврат восстанавливает SP и не допускает вложенный IRQ
;   код, изменяемые операнды и собственный стек доступны для записи, NMI и повторный вход не происходят
;   четыре части BcdCounter содержат допустимые упакованные десятичные пары для числового смысла счётчика
; Out:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX и IY восстановлены поверх результатов вызываемых процедур
;   SP равен исходному SP до аппаратного PUSH PC, продолжение исполняется через изменяемый JP, IFF разрешён инструкцией EI
;   CurrentPage и последний байт OUT #7FFD восстановлены к входной тени, предыдущее значение AY select не восстанавливается
;   обслужены независимые опросы ввода, указатель обновляется только при UpdateBlocked=0
;   при режиме #81 вызван музыкальный тик, иначе глушение AY зависит от сравнения с ModeOperand
;   делитель уменьшается по модулю 256, при достижении нуля перезагружается в 50 и увеличивает цепочку BCD
;   девять слов #A104..#A114 восстановлены исходными значениями #A0A6..#A0B6
; Corrupt:
;   нет изменяемых сохраняемых регистров при соблюдении договоров вызываемых процедур, R естественно продвигается, IFF становится разрешённым
; Note:
;   I сохраняется собственным кодом и подтверждёнными потребителями, вмешательство NMI этим договором исключено
;   StationIrqData.Storage содержит 26 байтов вложенных кадров и 22 байта сохранённого контекста
;   последним PUSH сохраняется полный байт CurrentPage в AF, нижний F этого слова нужен только как сохранённая часть
;   аппаратный адрес продолжения читается из прежнего стека до восстановления таблицы RET, затем SavedSP увеличивается на два
;   возврат через RET после ремонта таблицы прочитал бы восстановленное слово вместо аппаратного PC, поэтому применён LD SP,EI,JP
;   ModeOperand записывается значением #81 на музыкальной ветви, немузыкальная ветвь сохраняет прежний A, а не текущий режим C
;   если текущий немузыкальный режим отличается от ModeOperand, глушение выполняется повторно каждый вызов
;   Pulse получает перенос низшей BCD-пары только при срабатывании делителя, между срабатываниями прежний Pulse не очищается
;   низшая пара увеличивается раз в 50 вызовов после штатной перезагрузки, игровые единицы и нормализация потребителями отдельно не доказаны
;   модель исполняет опросы и указатель, музыкальный тик заменён договором, физические банки и аппаратный вход IM2 не эмулируются
; -----------------------------------------
                ; запрет повторного IRQ до завершения восстановления контекста и цепочки RET
Entry:          DI
                ; сохранение адреса аппаратного слова PC в изменяемом операнде SavedSP
                LD (@StationIrqState.SavedSP), SP
                ; выбор исходной вершины отдельного стека ISR над StationIrqData.Storage
                LD SP, @StationIrqData.StackTop
                ; создание физического кадра с основными, индексными и альтернативными регистрами
                PUSH IX
                PUSH IY
                PUSH AF
                PUSH HL
                PUSH DE
                PUSH BC
                EX AF, AF'
                PUSH AF
                EXX
                PUSH HL
                PUSH DE
                PUSH BC
                ; сохранение входной тени страницы поверх регистрового кадра
                LD A, (@StationState.CurrentPage)
                PUSH AF
                ; выбор станционного банка 0 с сохранением старших битов тени и установкой ROM 1
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; очистка шести общих входных флагов перед последовательными опросами
                CALL @Station.ClearInputFlags.Entry
                CALL @Station.PollJoystick.Entry
                CALL @Station.PollKeys.Entry
                CALL @Station.PollMouse.Entry
                ; чтение запрета рисования указателя из изменяемого операнда
                LD A, #00
                ; проверка запрета обновления после обработки всех источников ввода
                OR A
                JR NZ, @Station.Interrupt.ServiceSound                          ; переход, если UpdateBlocked ненулевой, пропустить UpdatePointer

                CALL @Station.UpdatePointer.Entry
                ; чтение целого кода музыкального режима, только #81 выбирает тик проигрывателя
ServiceSound:   LD A, (@StationIrqState.MusicMode)
                ; проверка специального кода музыкального режима
                CP @StationIrqConst.MusicMode
                JR Z, @Station.Interrupt.MusicMode                              ; переход, если режим равен #81, обслужить музыкальную ветвь

                LD C, A
                ; чтение прежнего операнда сравнения музыкальной ветви
                LD A, (@StationIrqState.ModeOperand)
                ; проверка равенства текущего режима C и прежнего операнда A
                CP C
                ; повторная запись прежнего A, текущий немузыкальный режим C здесь не сохраняется
                LD (@StationIrqState.ModeOperand), A
                JR Z, @Station.Interrupt.ClockTick                              ; переход, если текущий режим совпал с прежним операндом, пропустить глушение AY

                ; выбор регистра 7 AY перед сохранением его прежнего значения
                LD BC, #FFFD
                LD A, #07
                OUT (C), A
                IN A, (C)
                ; сохранение прежнего микшера в изменяемом операнде будущего восстановления
                LD (@StationIrqState.SavedMixer), A
                ; выбор значения #FF для закрытия всех тоновых и шумовых каналов микшером
                LD A, B
                LD B, #BF
                ; обновление микшера AY значением #FF
                OUT (C), A
                LD B, A
                ; глушение громкости канала A через регистр 8
                LD A, #08
                OUT (C), A
                XOR A
                LD B, #BF
                OUT (C), A
                LD B, #FF
                ; глушение громкости канала B через регистр 9
                LD A, #09
                OUT (C), A
                XOR A
                LD B, #BF
                OUT (C), A
                LD B, #FF
                ; глушение громкости канала C через регистр 10
                LD A, #0A
                OUT (C), A
                XOR A
                LD B, #BF
                OUT (C), A
                JR @Station.Interrupt.ClockTick

                ; сравнение режима #81 с прежним изменяемым операндом
MusicMode:      CP #00
                ; сохранение #81 в том же операнде независимо от результата сравнения
                LD (@StationIrqState.ModeOperand), A
                JR Z, @Station.Interrupt.PlayMusic                              ; переход, если прежний операнд уже равен #81, пропустить восстановление микшера

                ; выбор регистра 7 AY перед восстановлением сохранённого микшера
                LD BC, #FFFD
                LD A, #07
                OUT (C), A
                LD B, #BF
                ; чтение сохранённого значения микшера из изменяемого операнда
                LD A, #00
                OUT (C), A
                ; выбор банка 3 музыкального проигрывателя с установкой ROM 1
PlayMusic:      LD A, @StationIrqConst.MusicPage
                CALL @Station.SelectRamBank.Entry
                ; вызов кадрового входа PlayFrame выбранного музыкального банка
                CALL @Music.PlayFrame.Entry
                ; чтение текущего делителя обслуживания BCD-цепочки
ClockTick:      LD A, @StationIrqConst.ReloadFrames
                ; расчёт следующего делителя с байтовым переполнением при исходном нуле
                DEC A
                ; обновление изменяемого операнда делителя до проверки его нулевого результата
                LD (@StationIrqState.Divider), A
                JR NZ, @Station.Interrupt.RestoreContext                        ; переход, если делитель ещё ненулевой, пропустить BCD-цепочку

                ; перезагрузка исходного интервала 50 вызовов после достижения нуля
                LD A, @StationIrqConst.ReloadFrames
                LD (@StationIrqState.Divider), A
                ; чтение низшей упакованной десятичной пары
                LD A, (@StationTimer.Counter + FStationBcdCounter.Low)
                ; расчёт следующей низшей пары с последующей десятичной коррекцией
                ADD A, #01
                DAA
                LD (@StationTimer.Counter + FStationBcdCounter.Low), A
                ; подготовка Pulse=1 при переносе низшей пары, иначе значение уменьшается до нуля
                LD A, #01
                JR C, @Station.Interrupt.StorePulse                             ; переход, если низшая BCD-пара дала перенос, сохранить Pulse=1

                DEC A
                ; обновление запроса периодического прохода MainLoop только на срабатывании делителя
StorePulse:     LD (@StationIrqState.Pulse), A
                ; чтение следующей пары BCD перед прибавлением переноса
                LD A, (@StationTimer.Counter + FStationBcdCounter.MidLow)
                ; расчёт второй пары с переносом низшей и десятичной коррекцией
                ADC A, #00
                DAA
                LD (@StationTimer.Counter + FStationBcdCounter.MidLow), A
                ; чтение третьей пары BCD в необычном физическом порядке полей
                LD A, (@StationTimer.Counter + FStationBcdCounter.MidHigh)
                ; расчёт третьей пары с переносом второй и десятичной коррекцией
                ADC A, #00
                DAA
                LD (@StationTimer.Counter + FStationBcdCounter.MidHigh), A
                ; чтение старшей пары BCD
                LD A, (@StationTimer.Counter + FStationBcdCounter.High)
                ; расчёт старшей пары с переносом третьей, конечный перенос дальше не сохраняется
                ADC A, #00
                DAA
                LD (@StationTimer.Counter + FStationBcdCounter.High), A
                ; снятие сохранённой страницы из собственного кадра
RestoreContext: POP AF
                ; восстановление полного исходного байта страницы до ремонта внешнего стека
                CALL @Station.SelectMemoryPage.Entry
                ; чтение адреса аппаратного слова PC из сохранённого стека
                LD HL, (@StationIrqState.SavedSP)
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                ; сохранение SP до аппаратного PUSH PC, два байта возврата уже прочитаны в DE
                LD (@StationIrqState.SavedSP), HL
                ; сохранение аппаратного адреса продолжения в операнде финального JP до ремонта таблицы
                LD (@StationIrqState.ReturnPC), DE
                ; восстановление девяти исходных слов цепочки RET, аппаратный PUSH PC мог затереть одно из них
                LD HL, @Station.FillWindowBody.Scan1
                LD (@WindowFillChain.State + FWindowReturnChain.Row1), HL
                LD HL, @Station.FillWindowBody.Scan2
                LD (@WindowFillChain.State + FWindowReturnChain.Row2), HL
                LD HL, @Station.FillWindowBody.Scan3
                LD (@WindowFillChain.State + FWindowReturnChain.Row3), HL
                LD HL, @Station.FillWindowBody.Scan4
                LD (@WindowFillChain.State + FWindowReturnChain.Row4), HL
                LD HL, @Station.FillWindowBody.Scan5
                LD (@WindowFillChain.State + FWindowReturnChain.Row5), HL
                LD HL, @Station.FillWindowBody.Scan6
                LD (@WindowFillChain.State + FWindowReturnChain.Row6), HL
                LD HL, @Station.FillWindowBody.Scan7
                LD (@WindowFillChain.State + FWindowReturnChain.Row7), HL
                LD HL, @Station.FillWindowBody.AfterGroup
                LD (@WindowFillChain.State + FWindowReturnChain.AfterGroup), HL
                LD HL, @WindowFillConst.TailWordValue
                LD (@WindowFillChain.State + FWindowReturnChain.TailWord), HL
                ; восстановление альтернативных и основных регистров из собственного кадра
                POP BC
                POP DE
                POP HL
                EXX
                POP AF
                EX AF, AF'
                POP BC
                POP DE
                POP HL
                POP AF
                POP IY
                POP IX
                ; возврат исходного SP до аппаратного PUSH PC без чтения уже исправленной таблицы
                LD SP, #0000
                ; разрешение IRQ с задержкой до завершения следующего JP
                EI
                ; продолжение сохранённого аппаратного PC через изменяемый JP вместо RET
                JP #0000

                endmodule
                endmodule
