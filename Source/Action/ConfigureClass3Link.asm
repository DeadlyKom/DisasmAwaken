                module Action
                module ConfigureClass3Link
                ; Изменяемый порог [параметры и проверка](../../Docs/ActionParameterThresholds.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionClass3Link.md)
                ; -----------------------------------------
                ; Подстановка, фильтр классов 5 и 14 либо специальный код 26 по потоку 8
                ; исходная запись 17, адреса 65DE..660D
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord
                ;   LinkOverride, StateCode и LinkedIndex доступны по договору CopyRecordLinkOverride, он вызывается до иных проверок
                ;   действуют договоры вызываемых потоков и фильтров, достижима подходящая активная запись либо маркер
                ;   выбран ACTION банка 0, CPU-стек не пересекает запись, код и потоки, доступны 8 дополнительных байтов, IRQ не вмешиваются
                ; Out:
                ;   при LinkOverride=1..FE возвращается результат подстановки, LinkedIndex=LinkOverride и StateCode=02
                ;   при LinkOverride=0 либо FF обработка продолжается, разрешённый ноль сначала записывает LinkedIndex=0 и StateCode=02
                ;   после незавершившей подстановки читается R, StateCode=02 и LinkedIndex=FF записываются до выбора ветви
                ;   при R>=Class3RLimit выполняется поиск класса 5 либо 14 и при NZ записывается его A в LinkedIndex
                ;   при R<Class3RLimit нужны Gate>=40, Gate>=(LowWord(Stream8) AND FF) и старший байт нового слова Stream8<03, только тогда LinkedIndex=1A
                ;   при отказе специальных проверок LinkedIndex остаётся FF, Gate сохраняется через PUSH AF и POP AF вокруг настоящего потока 8
                ;   D, AF', IX, I/IM/IFF и paging сохраняются, SP после внешнего RET равен входному SP+2
                ;   при фильтре HL, E, BC, AF и IY соответствуют его договору, без фильтра E, BC и IY сохраняются
                ;   после генератора HL содержит новое слово последнего потока, HL', DE', BC' содержат его выход, до генератора они сохраняются
                ;   R и все флаги проверены точной числовой моделью каждого пути, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, E, BC, AF, HL', DE', BC', IY, R, StateCode, LinkedIndex, вызываемые состояния потоков и временные слова CPU-стека
                ; Note:
                ;   коды состояний и пороги в этой записи шестнадцатеричные, номера классов в названии десятичные
                ;   общий SelectLink может вернуть отдельный код 26, он не объявляется индексом найденной записи
                ;   совместная проверка восьми обработчиков исполнила 402384 сценария с настоящими детьми, точными регистрами, R, восемью банками и кратностью записей
                ;   охват конкретного входа и списков приведён в его отчёте, произведение всех состояний и списков не исчерпано
                ;   распределение аппаратного R, период генераторов, аппаратные IRQ, точные T, сборка и нативная игра не доказаны
                ;   после подстановки FF чтение R перед непосредственным CP происходит через 8 M1, после нуля через 14 M1
                ; -----------------------------------------
                ; Применение исходной подстановки до выбора состояния, ноль разрешён и продолжает обработку.
Entry:          CALL @Action.CopyRecordLinkOverride.Entry
                RET NZ                                                          ; выход, если LinkOverride находится в 1..FE, сохранить результат подстановки

                ; Выбор между обычным фильтром и специальной ветвью по аппаратному R.
                LD A, R
                CP @ActionClassSetupConst.EarlyRLimit
                ; Обновление StateCode=02 и LinkedIndex=FF до обеих ветвей.
                LD (IX + @FActionRecord.StateCode), @ActionClass0Const.RecordCode
                LD (IX + @FActionRecord.LinkedIndex), @ActionClass9Const.DefaultIndex
                JR C, @Action.ConfigureClass3Link.TryCode26                     ; переход, если прочитанный R меньше текущего Class3RLimit, проверить специальный код 26

                ; Поиск первого класса 5 либо 14 на обычной ветви R не меньше текущего Class3RLimit.
                CALL @Action.FindRecordClass5Or14.Entry
                RET Z                                                           ; выход, если фильтр классов 5 и 14 вернул Z, оставить LinkedIndex=FF

                ; Сохранение результата обычного фильтра после NZ.
                LD (IX + @FActionRecord.LinkedIndex), A
                RET

                ; Проверка существующего Gate по 9BCD перед вызовом потока 8.
TryCode26:      LD A, (@ActionPreferredChanceState.UnknownGate)
                CP @ActionClassSetupConst.GateMinimum
                RET C                                                           ; выход, если исходный Gate меньше 40, оставить LinkedIndex=FF

                ; Сохранение Gate и его флагов вокруг настоящего обновления Stream8.
                PUSH AF
                CALL @Action.NextRandomWord8.Entry
                ; Восстановление Gate после генератора и сравнение с младшим байтом нового слова.
                POP AF
                CP L
                RET C                                                           ; выход, если Gate меньше младшего байта нового слова Stream8, оставить LinkedIndex=FF

                ; Проверка старшего байта нового слова, допустимы только 00, 01 и 02.
                LD A, H
                CP @ActionClassSetupConst.HighLimit
                RET NC                                                          ; выход, если старший байт нового слова Stream8 не меньше 03, оставить LinkedIndex=FF

                ; Запись отдельного кода 1A, это исходный специальный результат, а не доказанный найденный индекс.
                LD (IX + @FActionRecord.LinkedIndex), @ActionRandomRecordConst.DefaultCode
                RET

                endmodule
                endmodule
