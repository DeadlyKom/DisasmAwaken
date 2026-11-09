                module Action
                module ToggleTractorMode
                ; Документация [команда силового луча](../../Docs/ActionTractorModeCommand.md)
                ; -----------------------------------------
                ; Переключение режима силового луча и запроса наведения со снятием захватов
                ; исходная запись 17, перенесённое ядро банка 5, адреса 7439..747F
                ; In:
                ;   HL, DE и BC задают сохраняемый контекст, AF входного аргумента не задаёт
                ;   CommandDelay допускает обработку только при нуле, TractorBeam.Value=FF означает отсутствие оборудования
                ;   банк 0 выбран, очередь Controls банка 1 удовлетворяет QueueTextItemBank1, paging разблокирован
                ;   CPU-стек допускает восемнадцать дополнительных байтов, IRQ не вмешиваются
                ; Out:
                ;   при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, записи и OUT отсутствуют
                ;   при нулевой задержке CommandDelay получает 10 до проверки оборудования
                ;   при TractorBeam.Value=FF HL, DE и BC сохраняются, A=0, F=50, остальные поля и paging не меняются
                ;   при допуске Mode по 7318 и Request по AA8E независимо получают прежний байт XOR 1, Target0..Target2 получают FF
                ;   CursorA получает EDA8, HL=EDA8, DE и BC сохраняются, A и F соответствуют XOR нового Request
                ;   порядок четырёх запросов очереди, состояние Mode, F2D9, состояние Request, F214
                ;   ненулевой результат каждого переключения выбирает F1E1, нулевой F1F0, приём четырёх запросов независим
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен исходному SP+2
                ;   восемь OUT 7FFD образуют четыре пары 11,10, итоговая страница 10, прежняя конфигурация не восстанавливается
                ; Corrupt:
                ;   HL, AF, R, CommandDelay, Mode, Request, захваты, CursorA, очередь, paging и восемнадцать временных байтов стека
                ; Note:
                ;   внутренний переход на ToggleTargetRequest.ToggleRequest пропускает его проверку задержки и установку задержки 7
                ;   после принятой команды остаётся задержка 10, четыре сообщения могут быть приняты частично
                ;   оба переключения сохраняют биты 7..1, произвольный ненулевой байт не превращается обязательно в ноль
                ;   3648 сценариев исполняют настоящий общий хвост и очередь, R, такты и остаточные слова временного стека не сверяются
                ; -----------------------------------------
                ; Проверка задержки перед изменением режима силового луча.
                ; Байт опкода 3A и младший байт адреса 5F также читаются как правила видов 28 и 29.
                ; Перекрытие [сбора объекта и кода](../../Docs/ActionTractorCollect.md), дополнительные байты не выводятся.
Entry:          LD A, (@ActionMissileLaunchState.CommandDelay)
                AND A
                RET NZ                                                          ; выход, если CommandDelay ненулевой, оба режима и захваты сохранить

                ; Обновление задержки до проверки установленного оборудования.
                LD A, #0A
                LD (@ActionMissileLaunchState.CommandDelay), A
                ; Проверка полного кода TractorBeam.Value, только FF означает отсутствие оборудования.
                LD A, (@ActionShipEquipment.TractorBeam.Value)
                INC A
                RET Z                                                           ; выход, если TractorBeam.Value равен FF, сохранить режимы при уже установленной задержке

                ; Выбор исходного звукового потока принятой команды в банке 0.
                LD HL, @ActionMissileCreateConst.ActionSound
                LD (@ActionAyEffectState.CursorA), HL
                ; Обновление бита 0 существующего операнда Mode, старшие биты сохраняются.
                LD A, (@ActionTractorModeState.Mode)
                XOR #01
                LD (@ActionTractorModeState.Mode), A
                ; Снятие всех трёх захватов до постановки сообщений.
                LD A, #FF
                LD (@ActionMissileTargets.Value.Target0), A
                LD (@ActionMissileTargets.Value.Target1), A
                LD (@ActionMissileTargets.Value.Target2), A
                JR Z, @Action.ToggleTractorMode.QueueDisabled                   ; переход, если новый Mode равен нулю, поставить сообщение о выключении

                ; Передача сообщения о включении силового луча с сохранением DE.
                PUSH DE
                LD DE, @ControlsFlightText.ModeEnabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                JR @Action.ToggleTractorMode.QueueBeamName

                ; Передача сообщения о выключении силового луча с сохранением DE.
QueueDisabled:  PUSH DE
                LD DE, @ControlsFlightText.ModeDisabled
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Передача названия режима отдельным запросом очереди.
QueueBeamName:  PUSH DE
                LD DE, @ControlsFlightText.TractorBeam
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                ; Продолжение во внутреннем входе переключения Request, повторная проверка задержки не выполняется.
                JP @Action.ToggleTargetRequest.ToggleRequest

                endmodule
                endmodule
