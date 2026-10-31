                module Station
                module MainLoop
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [изменяемые операнды и доказанные управляющие границы](../../Docs/MainLoopControl.md)
; -----------------------------------------
; Цикл станции, начальный и периодический сценарии, сравнение кодов ввода и событий
; исходная запись 4, файловые смещения #3A59..#3AE9
; In:
;   Unknown, регистровый контракт ещё не доказан
;   установлены управляющие предусловия, банк 0 содержит станционный код, исходные таблицы и операнды доступны для записи
;   HALT требует разрешённых прерываний и возвращающегося ISR, действует договор сохранения его контекста
;   GenerateMarket, RebuildInterface, DrawItem01, обработчики и сценарии должны сохранять продолжение, если возвращаются
; Out:
;   обычного общего RET нет, штатный путь повторяет Frame либо передаёт управление станционному переходу
;   до первого GenerateMarket TransitionCode=0, StationIrqState.Pulse=0, MarketState.MarkMode=80
;   после генерации MarkMode=0, начальный LANG-сценарий получает байт события 983A=0F
;   ненулевой Pulse сбрасывает Pulse и EventEnabled до периодического LANG-сценария с событием 10
;   после сценариев явный банковый интерфейс выбирает банк 0
;   TransitionCode=2..128 после DEC записывается уменьшенным и выбирает BeginTransition
;   TransitionCode=1 записывает 0 без перехода, коды 0 и 129..255 сохраняются без перехода
;   после MergeActionInputs C=текущий код, D=предыдущий код, PreviousAction получает текущий код
;   оба кода нулевые возвращают Frame, текущий меньше предыдущего вызывает CloseActiveItem, иначе DispatchInterfaceEvent
;   регистровый договор DrawItem01 установлен отдельно, полные эффекты всех изменяемых callback ещё не установлены
; Corrupt:
;   Unknown, эффекты всех сценариев и изменяемых callback должны быть уточнены до полного договора
; Note:
;   проверка управляющих границ не считается полным разбором всех исполняемых рисователей и событий
;   PeriodicCall и HoverCallback являются изменяемыми операндами CALL, исходные EmptyCallback не постоянные цели
;   HoverItem является операндом LD IX, после вызова HoverCallback его адрес безусловно сбрасывается на EmptyCallback
;   PreviousAction является операндом LD D, он читается до записи нового кода и не равен постоянному нулю
;   проверяется знак результата DEC TransitionCode, а не старший бит исходного байта
;   модель выполняет реальные инструкции выбора банка и MergeActionInputs, рисование, сценарии, ISR и callback не исполняет
; -----------------------------------------
                ; сброс кода запроса перехода и накопленного импульса перед первоначальным сценарием
Entry:          XOR A
                LD (@MainLoopState.TransitionCode), A
                LD (@StationIrqState.Pulse), A
                ; выбор маркирующего режима генерации начального рынка
                LD A, #80
                LD (@MarketState.MarkMode), A
                CALL @Station.GenerateMarket.Entry
                ; отключение начальной маркировки после GenerateMarket
                XOR A
                LD (@MarketState.MarkMode), A
                ; первоначальное перестроение списка и изображения интерфейса
                CALL @Station.RebuildInterface.Entry
                ; выбор банка LANG для сценария входа на станцию
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                ; запись исходного кода события входа на станцию перед интерпретатором
                LD A, #0F
                LD (@ScriptCallState.EventCode), A
                CALL @Text.RunMarketScript.Entry
                ; возврат банка станционного кода после сценария, если тот вернулся
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; чтение изменяемого операнда EventEnabled, ноль требует перестроения интерфейса
Frame:          LD A, #00
                ; проверка запроса перестроения до ожидания следующего прерывания
                AND A
                CALL Z, @Station.RebuildInterface.Entry                         ; вызов, если EventEnabled равен нулю, перестроить интерфейс
                ; ожидание прерывания, дальнейшая работоспособность зависит от настоящего ISR
                HALT
                ; вызов текущего PeriodicCall, исходная цель EmptyCallback может быть изменена
                CALL @Station.EmptyCallback.Entry
                ; чтение адреса наведённого элемента из изменяемого операнда HoverItem
                LD IX, #0000
                ; вызов текущего HoverCallback с подготовленным IX, исходная цель не постоянна
                CALL @Station.EmptyCallback.Entry
                ; сброс HoverCallback на пустой обработчик после его возможного однократного исполнения
                LD HL, #9A58
                LD (@InterfaceState.HoverCallback), HL
                ; проверка накопленного импульса обновления BCD-счётчика от ISR
CheckPulse:     LD A, #00
                OR A
                JR Z, @Station.MainLoop.CheckTransition                         ; переход, если Pulse равен нулю, не выполнять периодический сценарий

                ; сброс импульса и запроса готовности интерфейса до периодического сценария
                XOR A
                LD (@StationIrqState.Pulse), A
                LD (@InterfaceState.EventEnabled), A
                ; выбор банка LANG для периодического события
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                ; запись кода периодического события в общее поле сценария
                LD A, #10
                LD (@ScriptCallState.EventCode), A
                CALL @Text.RunMarketScript.Entry
                ; возврат станционного банка после периодического сценария
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; чтение изменяемого кода запроса перехода, это не доказанный обратный таймер
CheckTransition:LD A, #00
                ; расчёт кода на единицу меньше с байтовым оборачиванием
                DEC A
                JP M, @Station.MainLoop.PollActions                             ; переход, если результат DEC отрицателен, сохранить исходный код и опрашивать действия

                ; сохранение уменьшенного кода только при неотрицательном результате
                LD (@MainLoopState.TransitionCode), A
                JP NZ, @Station.HandleItem08.BeginTransition                    ; переход, если уменьшенный код ненулевой, исходный код 2..128 запрашивает выход станции

                ; сохранение текущего текстового окна перед обновлением статусного элемента 1
PollActions:    CALL @Station.SaveTextWindow.Entry
                CALL @Station.DrawItem01.Entry
                ; восстановление окна после рисователя перед опросом объединённого ввода
                CALL @Station.RestoreTextWindow.Entry
                ; объединение четырёх текущих источников ввода по договору MergeActionInputs
                CALL @Station.MergeActionInputs.Entry
                ; сохранение текущего кода в C перед чтением прошлого кода из операнда LD D
                LD C, A
                ; чтение PreviousAction, исходный ноль заменяется при каждом проходе опроса
                LD D, #00
                LD A, C
                ; обновление PreviousAction текущим кодом после чтения прежнего значения в D
                LD (@MainLoopState.PreviousAction), A
                ; проверка отсутствия как текущего, так и предыдущего кода
                OR D
                JP Z, @Station.MainLoop.Frame                                   ; переход, если оба кода равны нулю, продолжить ожидание кадра

                LD A, C
                ; сравнение текущего и предыдущего байтов как беззнаковых чисел
                CP D
                JP NC, @Station.MainLoop.DispatchAction                         ; переход, если текущий код не меньше предыдущего, вызвать диспетчер события

                ; закрытие активного элемента при уменьшении объединённого кода
                CALL @Station.CloseActiveItem.Entry
                JP @Station.MainLoop.Frame

                ; диспетчеризация при ненулевой паре кодов без уменьшения текущего значения
DispatchAction: CALL @Station.DispatchInterfaceEvent.Entry
                JP @Station.MainLoop.Frame

                endmodule
                endmodule
