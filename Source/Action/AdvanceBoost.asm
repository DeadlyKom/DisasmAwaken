                module Action
                module AdvanceBoost
                ; Документация [общий хвост ускорения, расход и шестнадцать шагов шкалы](../../Docs/ActionBoostAdvance.md)
                ; -----------------------------------------
                ; Общий хвост ускорения с фазовым расходом выбранного байта, созданием класса 20 и шестнадцатью шагами шкалы
                ; исходная запись 17, перенесённое ядро банка 5, адреса 7504..754B
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, вызывающий RequestBoost уже установил Request и не обнаружил препятствия
                ;   доступны Preferred и Fallback для SelectPreferredByte, Current, четыре фазовых операнда и LimitWord
                ;   действуют договоры ReleaseClass14Records, CreateRandomClass20Record и IncreaseGaugeWord.MotionGate
                ;   доступны список записей, Stream8 и коэффициенты преобразования, банк 0 выбран, стек допускает тридцать два дополнительных байта
                ;   IRQ и повторный вход исключены, размещение исходных операндов не изменяется
                ; Out:
                ;   SelectPreferredByte возвращает выбранный байт A и его адрес HL, C получает A-1 по модулю 256
                ;   при знаке C управление передаётся ReleaseClass14Records, допустимы только выбранные значения 1..128
                ;   FastPhase увеличивается по модулю 256, лишь при его переходе в ноль SlowPhase получает (старое+1) AND 7
                ;   лишь при двух нулевых результатах выбранный байт получает C, Current уменьшается по модулю 256, SecondRequest получает 1
                ;   FirstRotation вращается RRCA всегда на допущенном пути, SecondRotation вращается только при старом бите 0 FirstRotation
                ;   лишь при единичном старом бите 0 обоих вращений вызывается настоящий CreateRandomClass20Record, отказ выделения не отменяет дальнейшее ускорение
                ;   LimitWord получает 1000 после возможного создания записи, затем IncreaseGaugeWord.MotionGate вызывается шестнадцать раз
                ;   проверка SkipDetail по 7680 пропускается, MotionOpcode по 7685 всё ещё должен быть 3A для изменения SignedWord
                ;   на обычном завершении B=0, C сохранён из состояния перед циклом, прочие выходы соответствуют последнему шагу шкалы и возможному создателю
                ;   без создания альтернативные и индексные регистры сохраняются, при создании действуют его выходы, paging, I, IM и IFF сохраняются
                ;   внешний RET даёт SP=входной SP+2, знак ограничения проверяется исходной обёрнутой разностью, общего насыщения нет
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R по дочерним путям, выбранный байт, Current, фазовые операнды, запросы шкал, LimitWord, SignedWord, запись класса 20 и CPU-стек
                ; Note:
                ;   SecondRequest по 665C относится ко второй шкале, SignedWord дополнительно создаёт SixthRequest по 669F через ребёнка
                ;   ноль Current при расходе становится FF, верхние биты SlowPhase отбрасываются только при шаге FastPhase через ноль
                ;   изначальные фазы 00/00 и вращения 11/88 сохранены, имена описывают доказанные операции, физический смысл классов не выдумывается
                ;   69728 сквозных сценариев исполняют исходные оба фрагмента и настоящих детей, все пары Preferred/Fallback проверены
                ;   сверены регистры кроме R и тактов, все банки RAM и кратность записей вне тридцати двух временных байтов стека
                ;   полное произведение входов, IRQ, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Выбор существующего ненулевого Preferred либо Fallback вместе с адресом его физического байта.
Entry:          CALL @Action.SelectPreferredByte.Entry
                LD C, A
                ; Проверка знака выбранного значения после уменьшения, допускаются только исходные байты 1..128.
                DEC C
                JP M, @Action.ReleaseClass14Records.Entry                       ; переход, если A-1 имеет бит 7, освободить класс 14 без расхода и шагов шкалы

                ; Обновление быстрого фазового операнда по модулю 256.
StepFastPhase:  LD A, #00
                INC A
                LD (@ActionBoostState.FastPhase), A
                JR NZ, @Action.AdvanceBoost.RotateFirst                         ; переход, если FastPhase не перешёл в ноль, пропустить медленный шаг и расход

                ; Расчёт следующей медленной фазы, старшие пять битов отбрасываются маской 07.
StepSlowPhase:  LD A, #00
                INC A
                AND #07
                LD (@ActionBoostState.SlowPhase), A
                JR NZ, @Action.AdvanceBoost.RotateFirst                         ; переход, если SlowPhase ненулевой, пропустить расход выбранного байта

                ; Обновление выбранного байта и Current только при совпавшем нуле обеих фаз.
                LD (HL), C
                LD A, (@ActionByteLimitCounter.Value.Current)
                DEC A
                LD (@ActionByteLimitCounter.Value.Current), A
                ; Создание запроса второй шкалы после расхода, нулевой Current исходно оборачивается в FF.
                LD A, #01
                LD (@ActionPanelGaugesState.SecondRequest), A
                ; Расчёт первого кольцевого вращения, Carry содержит старый бит 0.
RotateFirst:    LD A, #11
                RRCA
                LD (@ActionBoostState.FirstRotation), A
                JR NC, @Action.AdvanceBoost.SetBoostLimit                       ; переход, если старый бит 0 FirstRotation сброшен, пропустить второе вращение и создание

                ; Расчёт второго вращения, его старый бит 0 допускает создание класса 20.
RotateSecond:   LD A, #88
                RRCA
                LD (@ActionBoostState.SecondRotation), A
                CALL C, @Action.CreateRandomClass20Record.Entry                 ; вызов, если старый бит 0 SecondRotation установлен, создать запись класса 20
                ; Обновление существующего LimitWord перед шестнадцатью шагами, новое размещение памяти не создаётся.
SetBoostLimit:  LD HL, #1000
                LD (@ActionControlDecayState.LimitWord), HL
                ; Подготовка шестнадцати вызовов внутреннего входа шкалы, проверка SkipDetail пропускается.
                LD B, #10
                ; Сохранение счётчика и младшего C вокруг каждого настоящего шага шкалы.
IncreaseLoop:   PUSH BC
                CALL @Action.IncreaseGaugeWord.MotionGate
                POP BC
                DJNZ @Action.AdvanceBoost.IncreaseLoop

                RET

                endmodule
                endmodule
